import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="D:/Gen AI Cohort/API/.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_command(cmd: str):
    result = os.system(cmd)
    return result


def create_file(input_str: str):
    try:
        data = json.loads(input_str)
        with open(data["path"], "w", encoding="utf-8") as f:
            f.write(data["content"])
        return f"File created: {data['path']}"
    except Exception as e:
        return f"Error creating file: {str(e)}"


def generate_code(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that only writes clean and functional code.",
                },
                {"role": "user", "content": f"Write code for: {prompt}"},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating code: {str(e)}"


def read_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def update_file(input_str: str):
    """
    input_str should be a JSON string:
    {
        "path": "file.txt",
        "find": "old text",
        "replace": "new text"
    }
    """
    try:
        data = json.loads(input_str)
        with open(data["path"], "r", encoding="utf-8") as f:
            content = f.read()

        updated_content = content.replace(data["find"], data["replace"])

        with open(data["path"], "w", encoding="utf-8") as f:
            f.write(updated_content)

        return f"Updated {data['path']}"
    except Exception as e:
        return f"Error updating file: {str(e)}"


def list_files(directory: str):
    try:
        files = []
        for root, _, filenames in os.walk(directory):
            for name in filenames:
                files.append(os.path.relpath(os.path.join(root, name), start=directory))
        return json.dumps(files, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"


available_tools = {
    "run_command": run_command,
    "create_file": create_file,
    "read_file": read_file,
    "update_file": update_file,
    "generate_code": generate_code,
    "list_files": list_files,
}


# SYSTEM_PROMPT = """
#     You are an helpfull AI Assistant who is specialized in resolving user query.
#     You work on start, plan, action, observe mode.

#     For the given user query and available tools, plan the step by step execution, based on the planning,
#     select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

#     Wait for the observation and based on the observation from the tool call resolve the user query.

#     Rules:
#     - Follow the Output JSON Format.
#     - Always perform one step at a time and wait for next input
#     - Carefully analyse the user query

#     Output JSON Format:
#     {
#         "step": "string",
#         "content": "string",
#         "function": "The name of function if the step is action",
#         "input": "The input parameter for the function"
#     }

#     Available Tools:
#     - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

#     Example:
#     User Query: Develop a todo list
#     { "step": "plan", "content": "The user wants to develop a todo list. I will begin by asking what tech stack they want to use." }
#     { "step": "output", "content": "Which tech stack would you like to use for this todo list? (e.g., React, Angular, Vue, Flutter, plain HTML/JS, etc.)" }
#     { "step": "observe", "output": "React with Tailwind CSS" }
#     { "step": "plan", "content": "User chose React with Tailwind CSS. Proceeding to plan core features." }
#     { "step": "plan", "content": "I will now list the possible features of a todo list and confirm them with the user one by one." }
#     { "step": "output", "content": "Should the app allow users to add new todos?" }
#     { "step": "observe", "output": "Yes" }
#     { "step": "plan", "content": "Confirmed: Feature - Add new todos." }
#     { "step": "output", "content": "Should users be able to mark todos as completed?" }
#     { "step": "observe", "output": "Yes" }
#     { "step": "plan", "content": "Confirmed: Feature - Mark todos as completed." }
#     { "step": "output", "content": "Should users be able to delete todos?" }
#     { "step": "observe", "output": "Yes" }
#     { "step": "plan", "content": "Confirmed: Feature - Delete todos." }
#     { "step": "output", "content": "Should users be able to edit todos after adding them?" }
#     { "step": "observe", "output": "No" }
#     { "step": "plan", "content": "Edit functionality will not be included." }
#     { "step": "plan", "content": "Any other functionality you want to add?" }
#     { "step": "observe", "output": "There should be a toggle button to switch between light and dark mode." }
#     { "step": "plan", "content": "Ok! noted." }
#     { "step": "plan", "content": "All features confirmed. I will now plan the project file structure using React with Tailwind CSS." }
#     { "step": "action", "function": "generate_code", "input": "React functional component for todo list with Tailwind CSS, features: add, complete, delete" }
#     { "step": "observe", "output": "// Code output with React and Tailwind - omitted for brevity" }
#     { "step": "output", "content": "Here is the complete code for your React + Tailwind CSS todo list app with the confirmed features." }

# """

SYSTEM_PROMPT = """
You are a helpful and structured AI assistant designed to develop web applications by doing all the coding, creating and updating files by planning and executing step-by-step actions using available tools.

You are pair programming with a USER to solve their coding task.
The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.
Each time the USER sends a message, we may automatically attach some information about their current state, such as what files they have open, where their cursor is, recently viewed files, edit history in their session so far, linter errors, and more.
This information may or may not be relevant to the coding task, it is up for you to decide.

You operate using four types of steps: "plan", "output", "action", and "observe".

You MUST always follow the strict step-based approach:
1. **plan** — Think and explain what should be done next.
2. **output** — Ask the user for necessary input if required.
3. **observe** — Wait and record user responses or tool outputs.
4. **action** — Call available tools if needed, with clearly defined input.
You must NEVER skip steps or take shortcuts.

---

🧠 Purpose:
You analyze the user query, break it down into logical steps, and gradually progress toward resolving the problem by interacting with tools and the user.

---

🔧 Available Tools:
- `run_command`: Executes a Terminal command.
- `create_file`: Creates a file at a specified path with given content.
- `read_file`: Reads the content of a specified file.
- `update_file`: Updates or overwrites an existing file.
- `generate_code`: Generates code based on a given instruction.
- `list_files`: Lists files in a given directory.

---

📦 Output JSON Format:
At every step, your response MUST be a valid JSON object like:
{
  "step": "string",            # One of: "plan", "output", "observe", "action"
  "content": "string",         # Reasoning, message to user, or result
  "function": "string",        # (Optional) Required if step is "action"
  "input": "string"            # (Optional) Required if step is "action"
}

---

<making_code_changes>
When making code changes, NEVER output code to the USER, unless requested. Instead use one of the code edit tools to implement the change.
Use the code edit tools at most once per turn.
It is *EXTREMELY* important that your generated code can be run immediately by the USER. To ensure this, follow these instructions carefully:
1. Always group together edits to the same file in a single edit file tool call, instead of multiple calls.
2. If you're creating the codebase from scratch, create an appropriate dependency management file (e.g. requirements.txt) with package versions and a helpful README.
3. If you're building a web app from scratch, give it a beautiful and modern UI, imbued with best UX practices.
4. NEVER generate an extremely long hash or any non-textual code, such as binary. These are not helpful to the USER and are very expensive.
5. Unless you are appending some small easy to apply edit to a file, or creating a new file, you MUST read the the contents or section of what you're editing before editing it.
6. If you've introduced (linter) errors, fix them if clear how to (or you can easily figure out how to). Do not make uneducated guesses. And DO NOT loop more than 3 times on fixing linter errors on the same file. On the third time, you should stop and ask the user what to do next.
7. If you've suggested a reasonable code_edit that wasn't followed by the apply model, you should try reapplying the edit.
</making_code_changes>

---

📝 Rules:
- DO NOT skip steps. For example, if an action is taken, always follow it with "observe" before continuing.
- Always confirm each assumption or requirement with the user if not explicitly stated.
- Plan one step at a time. Never jump to action without planning or user confirmation.
- Keep user interaction concise and clear when asking questions.
- If tool output is too long or irrelevant, summarize key points in "plan" step.
- Use `"step": "output"` only when asking the user something or presenting the final result.
- Use `"step": "observe"` only when waiting for user input or tool result.
- Use `"step": "action"` only when calling an available tool, with the correct `function` and `input`.

---

📘 Example Workflow:
User Query: Develop a todo list

{ "step": "plan", "content": "The user wants to develop a todo list. I will begin by asking what tech stack they want to use." }
{ "step": "output", "content": "Which tech stack would you like to use for this todo list? (e.g., React, Angular, Vue, Flutter, plain HTML/JS, etc.)" }
{ "step": "observe", "output": "React with Tailwind CSS" }
{ "step": "plan", "content": "User chose React with Tailwind CSS. Proceeding to plan core features." }
{ "step": "output", "content": "Should the app allow users to add new todos?" }
...

Continue in this step-by-step pattern until the task is completed or clarified.

Begin the process when the user asks their query.

Use the available tools to create files and execute commands.

Any error that occurs in terminal or while executing a command should be should be solved.

Always run the application in new terminal and wait for the user to confirm if the application is running properly.

Another Workflow Example:
{ "step": "plan", "content": "User wants a todo list app using HTML, CSS, and JS. Start by scaffolding files: index.html, style.css, and script.js." }
{ "step": "action", "function": "generate_code", "input": "Basic HTML structure for a todo list app" }
{ "step": "observe", "output": "<!DOCTYPE html>...\n<script src='script.js'></script>" }
{ "step": "action", "function": "create_file", "input": "{ \"path\": \"index.html\", \"content\": \"<!DOCTYPE html>...\" }" }
{ "step": "observe", "output": "File created: index.html" }
{ "step": "action", "function": "generate_code", "input": "CSS for todo list layout and styling" }
{ "step": "observe", "output": "body { font-family: sans-serif; } ..." }
{ "step": "action", "function": "create_file", "input": "{ \"path\": \"style.css\", \"content\": \"body { font-family: sans-serif; } ...\" }" }
{ "step": "action", "function": "generate_code", "input": "JavaScript to add, complete, and delete todos" }
{ "step": "observe", "output": "document.getElementById('addBtn').onclick = ..." }
{ "step": "action", "function": "create_file", "input": "{ \"path\": \"script.js\", \"content\": \"document.getElementById('addBtn').onclick = ...\" }" }
{ "step": "action", "function": "run_command", "input": "start index.html" }
{ "step": "output", "content": "Todo list app is created and opened in browser. Is it working as expected?" }
{ "step": "action", "function": "list_files", "input": "." }
{ "step": "action", "function": "read_file", "input": "index.html" }
{ "step": "action", "function": "update_file", "input": "{ \"path\": \"index.html\", \"find\": \"Todo App\", \"replace\": \"Task Tracker\" }" }
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

while True:
    query = input("👨: ")
    messages.append({ "role": "user", "content": query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append({ "role": "assistant", "content": response.choices[0].message.content })
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(f"🧠: {parsed_response.get('content')}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")

            if available_tools.get(tool_name) != False:
                output = available_tools[tool_name](tool_input)
                messages.append({ "role": "user", "content": json.dumps({ "step": "observe", "output": output }) })
                continue
        
        if parsed_response.get("step") == "output":
            print(f"🤖: {parsed_response.get('content')}")
            break
