import json
import subprocess
import os
from aras.agent.llm import LLMClient
from aras.workspace.manager import WorkspaceManager

class ArasAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.workspace = WorkspaceManager()
        self.system_prompt = """
        You are Aras, a highly advanced autonomous AI agent running in a Termux environment.
        You possess deep reasoning capabilities and can execute complex multi-step plans.
        
        Your core capabilities include:
        1.  **Workspace Management**: Create, read, update, and delete files in 'aras-workspace'.
        2.  **Terminal Execution**: Run shell commands, install packages, and manage processes.
        3.  **App Development**: Create and run React (Vite/Next.js) or pure HTML/JS apps.
        4.  **Chain of Thought**: Break down complex requests into logical steps.
        
        Available Tools:
        - list_files: List files in the workspace.
        - read_file(file_path): Read file content.
        - write_file(file_path, content): Write/Update file content.
        - delete_file(file_path): Delete a file or directory.
        - execute_command(command): Run a shell command in the workspace.
        - run_app(app_dir, port): Start a development server (e.g., 'npm run dev').
        - stop_app(port): Stop a running app on a specific port.
        
        CRITICAL GUIDELINES:
        - Always respond in JSON format.
        - Use "thought" to explain your reasoning before taking action.
        - If a task is complex, use "plan" to outline your steps.
        - Use "tool" and "args" to perform actions.
        - Use "answer" only when the entire task is complete.
        - You can execute multiple tools sequentially.
        
        Example JSON:
        {
            "thought": "I need to create a React app and then start the dev server.",
            "plan": ["Create project structure", "Install dependencies", "Start dev server"],
            "tool": "execute_command",
            "args": {"command": "npx create-vite my-app --template react-ts"}
        }
        """

    def execute_tool(self, tool_name, args):
        print(f"[*] Executing tool: {tool_name} with args: {args}")
        try:
            if tool_name == "list_files":
                return self.workspace.list_files()
            elif tool_name == "read_file":
                return self.workspace.read_file(args.get("file_path"))
            elif tool_name == "write_file":
                return self.workspace.write_file(args.get("file_path"), args.get("content"))
            elif tool_name == "delete_file":
                return self.workspace.delete_file(args.get("file_path"))
            elif tool_name == "execute_command":
                cmd = args.get("command")
                # Run command in workspace directory
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, 
                    cwd=self.workspace.workspace_path, timeout=120
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
            elif tool_name == "run_app":
                app_dir = args.get("app_dir", ".")
                port = args.get("port", 3000)
                # This would typically start a background process
                # For Termux, we'll use a simplified version
                full_app_path = self.workspace.workspace_path / app_dir
                cmd = f"cd {full_app_path} && npm run dev -- --port {port} &"
                subprocess.Popen(cmd, shell=True, cwd=full_app_path)
                return f"App starting on port {port} in background."
            elif tool_name == "stop_app":
                port = args.get("port")
                subprocess.run(f"fuser -k {port}/tcp", shell=True)
                return f"Stopped app on port {port}."
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Tool execution error: {str(e)}"

    def process_query(self, query):
        print(f"[Aras] Processing: {query}")
        
        # Initial reasoning
        response = self.llm.chat(query, system_prompt=self.system_prompt)
        
        # Multi-step loop
        for step in range(15): # Increased steps for advanced tasks
            if "tool" in response:
                tool_result = self.execute_tool(response["tool"], response.get("args", {}))
                # Feed result back to agent
                response = self.llm.chat(f"Tool result: {json.dumps(tool_result)}")
            elif "answer" in response:
                return response["answer"]
            else:
                # Fallback if JSON is malformed or missing keys
                return response.get("content", "Task completed or waiting for input.")
        
        return "Maximum reasoning steps reached. Please refine your request."

def start_local_chat():
    agent = ArasAgent()
    print("\n--- Aras Advanced AI Agent ---")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            query = input("User > ")
            if query.lower() in ["exit", "quit"]:
                break
            answer = agent.process_query(query)
            print(f"\nAras > {answer}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[!] Error: {e}\n")
