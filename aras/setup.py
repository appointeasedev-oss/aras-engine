import os
from pathlib import Path
from aras.config import load_config, save_config

def setup_workspace():
    config = load_config()
    workspace_path = Path(config.get("workspace_path", Path.home() / "aras-workspace"))
    
    # Create the workspace directory
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"Created workspace at: {workspace_path}")
    else:
        print(f"Workspace already exists at: {workspace_path}")
    
    # In Termux, we might need to request storage access
    # termux-setup-storage creates a 'storage' symlink in home
    storage_link = Path.home() / "storage"
    if not storage_link.exists():
        print("Tip: Run 'termux-setup-storage' in Termux to allow access to your device's internal storage.")
    
    # Ensure the config directory exists
    config_dir = Path.home() / ".aras"
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created config directory at: {config_dir}")
    
    save_config(config)
    print("Setup complete!")
