import json
import subprocess
import os
import sys
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
        - You can execute only ONE tool per response.
        - If you don't need a tool, just provide "thought" and "answer".
        
        Example JSON for tool use:
        {
            "thought": "I need to create a React app.",
            "plan": ["Create project structure", "Install dependencies", "Start dev server"],
            "tool": "execute_command",
            "args": {"command": "npx create-vite my-react-app --template react-ts"}
        }

        Example JSON for final answer:
        {
            "thought": "I have created the file as requested.",
            "answer": "The file 'hello.html' has been created in the workspace."
        }
        """

    def execute_tool(self, tool_name, args):
        print(f"[*] Executing tool: {tool_name} with args: {args}")
        if not tool_name or tool_name.lower() == "none":
            return "No tool executed."

        try:
            # Normalizing argument names: some models use 'path' instead of 'file_path'
            file_path = args.get("file_path") or args.get("path")
            
            if tool_name == "list_files":
                return self.workspace.list_files()
            elif tool_name == "read_file":
                return self.workspace.read_file(file_path)
            elif tool_name == "write_file":
                return self.workspace.write_file(file_path, args.get("content"))
            elif tool_name == "delete_file":
                return self.workspace.delete_file(file_path)
            elif tool_name == "execute_command":
                cmd = args.get("command")
                # Run command in workspace directory
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, 
                    cwd=self.workspace.workspace_path, timeout=600 # 10 mins for heavy tasks
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
            elif tool_name == "run_app":
                app_dir = args.get("app_dir", ".")
                port = args.get("port", 3000)
                full_app_path = self.workspace.workspace_path / app_dir
                # Use nohup to keep it running and redirect output
                cmd = f"nohup npm run dev -- --port {port} > app.log 2>&1 &"
                subprocess.Popen(cmd, shell=True, cwd=full_app_path)
                return f"App starting on port {port} in background. Check app.log for details."
            elif tool_name == "stop_app":
                port = args.get("port")
                # More robust way to kill process on port
                subprocess.run(f"fuser -k {port}/tcp", shell=True)
                return f"Stopped app on port {port}."
            else:
                return f"Error: Unknown tool '{tool_name}'."
        except Exception as e:
            return f"Tool execution error: {str(e)}"

    def process_query(self, query):
        print(f"[Aras] Processing: {query}")
        
        # Initial reasoning
        response = self.llm.chat(query, system_prompt=self.system_prompt)
        
        # Multi-step loop
        for step in range(20): 
            if "tool" in response and response["tool"] and response["tool"].lower() != "none":
                tool_result = self.execute_tool(response["tool"], response.get("args", {}))
                # Feed result back to agent
                response = self.llm.chat(f"Tool result: {json.dumps(tool_result)}")
            elif "answer" in response:
                return response["answer"]
            else:
                # If no tool and no answer, but has thought, it might be stuck or finished without 'answer' key
                if "thought" in response and not any(k in response for k in ["tool", "answer"]):
                     # Try one more chat to get the answer
                     response = self.llm.chat("Please provide the final answer if you are done, or use a tool if needed.")
                else:
                    return response.get("content", "Task completed.")
        
        return "Maximum reasoning steps reached. Please refine your request."
