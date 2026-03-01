import os
import shutil
from pathlib import Path
from aras.config import load_config

class WorkspaceManager:
    def __init__(self):
        config = load_config()
        self.workspace_path = Path(config.get("workspace_path", Path.home() / "aras-workspace"))
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    def list_files(self):
        files = []
        for root, dirs, filenames in os.walk(self.workspace_path):
            # Exclude hidden files and common ignore dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'dist', 'build']]
            for filename in filenames:
                if not filename.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_path)
                    files.append(rel_path)
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

    def create_react_app(self, app_name):
        # In a real Termux environment, we'd run 'npx create-react-app'
        # For now, we'll simulate by creating a basic structure
        app_path = self.workspace_path / app_name
        app_path.mkdir(parents=True, exist_ok=True)
        
        # Create a simple index.html and package.json as a placeholder
        self.write_file(f"{app_name}/index.html", "<html><body><div id='root'></div></body></html>")
        self.write_file(f"{app_name}/package.json", '{"name": "' + app_name + '", "version": "1.0.0"}')
        
        return f"Created React app structure in {app_name}"
