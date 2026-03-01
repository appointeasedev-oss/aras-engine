import requests
import json
import time
import os
import re
from pathlib import Path
from aras.config import load_config

class LLMClient:
    def __init__(self):
        config = load_config()
        self.api_keys = config.get("openrouter_api_keys", [])
        self.models = config.get("models", [])
        self.history_dir = Path.home() / ".aras" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / f"session_{int(time.time())}.json"
        self.history = []

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def chat(self, prompt, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add history to messages
        messages.extend(self.history)
        messages.append({"role": "user", "content": prompt})
        
        if not self.api_keys:
            raise Exception("No OpenRouter API keys configured. Run 'aras models' to add keys.")
        
        if not self.models:
            raise Exception("No models configured. Run 'aras models' to add models.")

        for key in self.api_keys:
            for model in self.models:
                try:
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://github.com/appointeasedev-oss/aras-engine",
                            "X-Title": "Aras Engine"
                        },
                        data=json.dumps({
                            "model": model,
                            "messages": messages,
                            # Remove response_format if it causes issues, or keep it if model supports it
                            # "response_format": {"type": "json_object"} 
                        }),
                        timeout=120 
                    )
                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Enhanced JSON extraction
                        json_content = None
                        
                        # Try direct parse
                        try:
                            json_content = json.loads(content)
                        except json.JSONDecodeError:
                            # Try regex extraction
                            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                            if json_match:
                                try:
                                    json_content = json.loads(json_match.group(1))
                                except:
                                    pass
                        
                        if json_content is None:
                            # If still no JSON, wrap content in a thought
                            json_content = {"thought": "The model did not provide a valid JSON response.", "answer": content}
                        
                        # Update history
                        self.history.append({"role": "user", "content": prompt})
                        self.history.append({"role": "assistant", "content": content})
                        self.save_history()
                        
                        return json_content
                    else:
                        print(f"Error with model {model}: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"Exception with model {model}: {e}")
                time.sleep(1)
        
        raise Exception("All API keys and models failed.")
