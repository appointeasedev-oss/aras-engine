import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".aras"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        return {
            "telegram_bot_token": "",
            "allowed_user_ids": [],
            "openrouter_api_keys": [],
            "models": ["arcee-ai/trinity-large-preview:free", "liquid/lfm-2.5-1.2b-thinking:free"],
            "workspace_path": str(Path.home() / "aras-workspace")
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def configure_settings():
    config = load_config()
    print("--- Aras Configuration ---")
    config["telegram_bot_token"] = input(f"Enter Telegram Bot Token [{config['telegram_bot_token']}]: ") or config["telegram_bot_token"]
    
    user_ids = input(f"Enter Allowed User IDs (comma separated) [{','.join(map(str, config['allowed_user_ids']))}]: ")
    if user_ids:
        config["allowed_user_ids"] = [int(uid.strip()) for uid in user_ids.split(",") if uid.strip().isdigit()]
    
    save_config(config)
    print("Configuration saved!")

def manage_models():
    config = load_config()
    print("--- Aras Models & API Keys ---")
    
    keys = input(f"Enter OpenRouter API Keys (comma separated) [{','.join(config['openrouter_api_keys'])}]: ")
    if keys:
        config["openrouter_api_keys"] = [k.strip() for k in keys.split(",") if k.strip()]
    
    models = input(f"Enter Models (comma separated) [{','.join(config['models'])}]: ")
    if models:
        config["models"] = [m.strip() for m in models.split(",") if m.strip()]
    
    save_config(config)
    print("Models and API keys updated!")
