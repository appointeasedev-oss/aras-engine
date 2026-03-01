import json
from aras.agent.llm import LLMClient
from aras.workspace.manager import WorkspaceManager

class ArasAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.workspace = WorkspaceManager()
        self.system_prompt = """
        You are Aras, an autonomous AI agent running in a Termux environment.
        You can think, reason, and perform multiple API calls to solve complex tasks.
        You have access to a workspace where you can create React apps or pure HTML/CSS/JS apps.
        
        Available Tools:
        1. list_files: List all files in the workspace.
        2. read_file(file_path): Read the content of a file.
        3. write_file(file_path, content): Write content to a file.
        4. delete_file(file_path): Delete a file or directory.
        5. create_react_app(app_name): Create a basic React app structure.
        
        CRITICAL:
        - Always respond in JSON format.
        - If you need to use a tool, include "tool" and "args" in your JSON.
        - If you have a final answer, include "answer" in your JSON.
        - You can perform multiple steps. After each tool use, you will receive the result and can continue thinking.
        
        Example JSON for tool use:
        {
            "thought": "I need to see what files are in the workspace.",
            "tool": "list_files",
            "args": {}
        }
        
        Example JSON for final answer:
        {
            "thought": "I have finished creating the app.",
            "answer": "The React app 'my-app' has been created in the workspace."
        }
        """

    def process_query(self, query):
        print(f"Processing query: {query}")
        
        # Initial call to LLM
        response = self.llm.chat(query, system_prompt=self.system_prompt)
        
        # Multi-call loop (max 10 steps)
        for _ in range(10):
            if "tool" in response:
                tool_name = response["tool"]
                args = response.get("args", {})
                
                print(f"Using tool: {tool_name} with args: {args}")
                
                # Execute tool
                if tool_name == "list_files":
                    result = self.workspace.list_files()
                elif tool_name == "read_file":
                    result = self.workspace.read_file(args.get("file_path"))
                elif tool_name == "write_file":
                    result = self.workspace.write_file(args.get("file_path"), args.get("content"))
                elif tool_name == "delete_file":
                    result = self.workspace.delete_file(args.get("file_path"))
                elif tool_name == "create_react_app":
                    result = self.workspace.create_react_app(args.get("app_name"))
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Send result back to LLM
                response = self.llm.chat(f"Tool result: {result}")
            elif "answer" in response:
                return response["answer"]
            else:
                return response.get("content", "I'm not sure how to respond.")
        
        return "I reached the maximum number of steps without a final answer."

def start_local_chat():
    agent = ArasAgent()
    print("--- Aras Local Chat ---")
    print("Type 'exit' to quit.")
    while True:
        try:
            query = input("You: ")
            if query.lower() == "exit":
                break
            answer = agent.process_query(query)
            print(f"Aras: {answer}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
