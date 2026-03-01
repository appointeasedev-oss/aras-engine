import requests
import json
import time
from aras.config import load_config

class LLMClient:
    def __init__(self):
        config = load_config()
        self.api_keys = config.get("openrouter_api_keys", [])
        self.models = config.get("models", [])
        self.history = []

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
                        },
                        data=json.dumps({
                            "model": model,
                            "messages": messages,
                            "response_format": {"type": "json_object"}
                        }),
                        timeout=60 
                    )
                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Try to parse JSON content
                        try:
                            json_content = json.loads(content)
                        except json.JSONDecodeError:
                            import re
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                try:
                                    json_content = json.loads(json_match.group())
                                except:
                                    json_content = {"content": content}
                            else:
                                json_content = {"content": content}
                        
                        # Update history
                        self.history.append({"role": "user", "content": prompt})
                        self.history.append({"role": "assistant", "content": content})
                        
                        return json_content
                    else:
                        print(f"Error with model {model}: {response.text}")
                except Exception as e:
                    print(f"Exception with model {model}: {e}")
                time.sleep(1)
        
        raise Exception("All API keys and models failed.")
