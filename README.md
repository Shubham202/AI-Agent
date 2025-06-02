# 🧠 AI Coding Assistant (Step-Based Agent)

This project is an **AI-powered code generation and execution agent** that follows a strict `plan → output → observe → action` methodology to interactively build and manage codebases with the help of OpenAI's GPT models.

It enables dynamic and guided coding sessions using tools like file operations, terminal command execution, and code generation—all orchestrated through structured JSON responses.

---

## 📌 Features

- ✅ Step-by-step AI reasoning and execution
- 🛠️ Tools for:
  - Running terminal commands
  - Creating and updating files
  - Listing directory structure
  - Reading and modifying files
  - Generating clean and functional code using OpenAI's GPT
- 🔁 Looping mechanism until task completion
- 📄 JSON-based agent communication format
- 🤖 Modular tool handling and prompt engineering

---

## 🚀 How It Works

The assistant follows a structured workflow for every user query:

1. **Plan**: Analyze the task and decide the next step.
2. **Output**: Ask the user for required information.
3. **Observe**: Wait for user input or tool result.
4. **Action**: Execute a tool based on the plan.

Example:
```json
{ "step": "plan", "content": "User wants a todo list app. Let's ask for tech stack." }
{ "step": "output", "content": "Which tech stack would you like to use?" }
{ "step": "observe", "output": "React with Tailwind" }
{ "step": "action", "function": "generate_code", "input": "React todo app with Tailwind" }