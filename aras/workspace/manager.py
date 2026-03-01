import os
import shutil
import subprocess
from pathlib import Path
from aras.config import load_config

class WorkspaceManager:
    def __init__(self):
        config = load_config()
        self.workspace_path = Path(config.get("workspace_path", Path.home() / "aras-workspace"))
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    def list_files(self, recursive=True):
        files = []
        for root, dirs, filenames in os.walk(self.workspace_path):
            # Exclude hidden files and common ignore dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'dist', 'build', '.git']]
            for filename in filenames:
                if not filename.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_path)
                    files.append(rel_path)
            if not recursive:
                break
        return files

    def read_file(self, file_path):
        full_path = self.workspace_path / file_path
        if full_path.exists() and full_path.is_file():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {e}"
        return "File not found."

    def write_file(self, file_path, content):
        full_path = self.workspace_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def delete_file(self, file_path):
        full_path = self.workspace_path / file_path
        if full_path.exists():
            try:
                if full_path.is_file():
                    full_path.unlink()
                else:
                    shutil.rmtree(full_path)
                return f"Successfully deleted {file_path}"
            except Exception as e:
                return f"Error deleting file: {e}"
        return "File not found."

    def create_project(self, project_type, project_name):
        """
        Advanced project creation using real tools if available.
        """
        project_path = self.workspace_path / project_name
        if project_type == "react":
            # Use Vite for fast React setup
            cmd = f"npx create-vite {project_name} --template react-ts"
            result = subprocess.run(cmd, shell=True, cwd=self.workspace_path, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Created React (Vite) project: {project_name}"
            else:
                return f"Error creating React project: {result.stderr}"
        elif project_type == "html":
            project_path.mkdir(parents=True, exist_ok=True)
            self.write_file(f"{project_name}/index.html", "<!DOCTYPE html><html><head><title>Aras App</title></head><body><h1>Hello from Aras!</h1></body></html>")
            self.write_file(f"{project_name}/style.css", "body { font-family: sans-serif; }")
            self.write_file(f"{project_name}/script.js", "console.log('Aras App Loaded');")
            return f"Created pure HTML/CSS/JS project: {project_name}"
        else:
            return f"Unknown project type: {project_type}"
