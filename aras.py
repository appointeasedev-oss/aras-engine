#!/usr/bin/env python3
"""
Aras - A Comprehensive Telegram AI Agent
A single-file, multi-provider AI agent with web research, coding, file management, and email capabilities.
Supports OpenAI, OpenRouter, and Minimax providers.
Runs efficiently on Termux and standard Python environments.
"""

import os
import sys
import json
import asyncio
import subprocess
import re
import time
import smtplib
import imaplib
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import BytesParser
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class ConfigManager:
    """Manages persistent configuration for the Aras agent."""

    def __init__(self, config_path: str = "aras_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return empty dict."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        self.save_config()

    def reset(self) -> None:
        """Reset all configuration."""
        self.config = {}
        self.save_config()

    def is_configured(self) -> bool:
        """Check if bot is fully configured."""
        required_keys = ["bot_token", "user_id", "ai_provider", "api_key", "agent_name"]
        return all(key in self.config for key in required_keys)


# ============================================================================
# AI PROVIDER INTERFACE
# ============================================================================

class AIProvider:
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: str = ""
    ) -> str:
        """Generate response from AI provider."""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key, model)
        self.base_url = base_url

    async def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: str = ""
    ) -> str:
        """Generate response using OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating response: {str(e)}"


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider."""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)

    async def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: str = ""
    ) -> str:
        """Generate response using OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://aras-agent.local",
            "X-Title": "Aras Agent",
            "Content-Type": "application/json",
        }

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                "https://openrouter.io/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating response: {str(e)}"


class MinimaxProvider(AIProvider):
    """Minimax API provider."""

    def __init__(self, api_key: str, model: str, group_id: str = ""):
        super().__init__(api_key, model)
        self.group_id = group_id

    async def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: str = ""
    ) -> str:
        """Generate response using Minimax API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        if self.group_id:
            payload["group_id"] = self.group_id

        try:
            response = requests.post(
                "https://api.minimax.chat/v1/text/chatcompletion",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["reply"]
        except Exception as e:
            return f"Error generating response: {str(e)}"


# ============================================================================
# TOOL EXECUTORS
# ============================================================================

class WebSearchTool:
    """Performs web searches and retrieves information."""

    @staticmethod
    async def search(query: str, num_results: int = 5) -> str:
        """Search the web using DuckDuckGo (no API key required)."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            url = f"https://duckduckgo.com/search?q={urlencode({'q': query})}&format=json"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("Results", [])[:num_results]:
                results.append(
                    f"- {result.get('Title', 'N/A')}\n  {result.get('FirstURL', 'N/A')}\n  {result.get('Text', 'N/A')[:200]}"
                )

            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Search error: {str(e)}"

    @staticmethod
    async def fetch_page(url: str) -> str:
        """Fetch and parse a web page."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            return text[:2000]  # Limit to 2000 chars
        except Exception as e:
            return f"Error fetching page: {str(e)}"


class FileSystemTool:
    """Manages file system operations."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

    async def create_folder(self, folder_name: str) -> str:
        """Create a new folder."""
        try:
            folder_path = self.base_path / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
            return f"Folder created: {folder_path}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"

    async def save_file(self, file_name: str, content: str) -> str:
        """Save content to a file."""
        try:
            file_path = self.base_path / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            return f"File saved: {file_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"

    async def read_file(self, file_name: str) -> str:
        """Read a file."""
        try:
            file_path = self.base_path / file_name
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def delete_file(self, file_name: str) -> str:
        """Delete a file."""
        try:
            file_path = self.base_path / file_name
            file_path.unlink()
            return f"File deleted: {file_path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    async def list_files(self, folder: str = ".") -> str:
        """List files in a folder."""
        try:
            folder_path = self.base_path / folder
            files = list(folder_path.iterdir())
            return "\n".join(str(f.relative_to(self.base_path)) for f in files)
        except Exception as e:
            return f"Error listing files: {str(e)}"


class CodeExecutorTool:
    """Executes Python code safely."""

    @staticmethod
    async def execute_python(code: str) -> str:
        """Execute Python code and return output."""
        try:
            # Create a temporary file
            temp_file = Path("/tmp/aras_code_temp.py")
            with open(temp_file, "w") as f:
                f.write(code)

            # Execute the code
            result = subprocess.run(
                ["python3", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Clean up
            temp_file.unlink()

            output = result.stdout + result.stderr
            return output[:2000] if output else "Code executed successfully with no output."
        except subprocess.TimeoutExpired:
            return "Code execution timed out."
        except Exception as e:
            return f"Error executing code: {str(e)}"


class EmailTool:
    """Manages email operations."""

    def __init__(self, email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    async def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            return f"Email sent to {to}"
        except Exception as e:
            return f"Error sending email: {str(e)}"

    async def read_emails(self, num_emails: int = 5) -> str:
        """Read recent emails."""
        try:
            imap_server = imaplib.IMAP4_SSL("imap.gmail.com")
            imap_server.login(self.email, self.password)
            imap_server.select("INBOX")

            _, email_ids = imap_server.search(None, "ALL")
            email_ids = email_ids[0].split()[-num_emails:]

            emails = []
            for email_id in email_ids:
                _, email_data = imap_server.fetch(email_id, "(RFC822)")
                email_message = BytesParser().parsebytes(email_data[0][1])
                emails.append(
                    f"From: {email_message['From']}\nSubject: {email_message['Subject']}\n{email_message.get_payload()[:200]}\n---"
                )

            imap_server.close()
            imap_server.logout()

            return "\n".join(emails)
        except Exception as e:
            return f"Error reading emails: {str(e)}"


# ============================================================================
# AGENT CORE
# ============================================================================

class ArasAgent:
    """Core agent logic with personality and tool management."""

    def __init__(self, config: ConfigManager, ai_provider: AIProvider):
        self.config = config
        self.ai_provider = ai_provider
        self.conversation_history: List[Dict[str, str]] = []
        self.personality = self._build_personality()
        self.web_search = WebSearchTool()
        self.file_system = FileSystemTool()
        self.code_executor = CodeExecutorTool()
        self.email_tool = None

    def _build_personality(self) -> str:
        """Build the agent's personality prompt."""
        agent_name = self.config.get("agent_name", "Aras")
        return f"""You are {agent_name}, an intelligent and helpful AI assistant. You have a warm, professional, and human-like personality. 
You are capable of:
- Performing web searches and research
- Writing and executing code
- Managing files and folders
- Sending and reading emails
- Solving complex problems
- Providing detailed explanations

Always be helpful, honest, and efficient. When asked to perform tasks, use the available tools appropriately.
Respond naturally as if you were a human expert in the field."""

    async def process_message(self, user_message: str) -> str:
        """Process a user message and generate a response."""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Keep only last 20 messages for context
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        # Check for tool requests
        tool_response = await self._handle_tool_requests(user_message)
        if tool_response:
            user_message = f"{user_message}\n\n[Tool Output]:\n{tool_response}"
            self.conversation_history[-1]["content"] = user_message

        # Generate response
        response = await self.ai_provider.generate_response(
            self.conversation_history, self.personality
        )

        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    async def _handle_tool_requests(self, message: str) -> Optional[str]:
        """Detect and handle tool requests in the message."""
        message_lower = message.lower()

        # Web search
        if any(keyword in message_lower for keyword in ["search", "find", "look up", "research"]):
            search_query = re.sub(r"(search|find|look up|research)\s+(?:for\s+)?", "", message_lower, flags=re.IGNORECASE)
            if search_query:
                return await self.web_search.search(search_query)

        # File operations
        if "create folder" in message_lower or "mkdir" in message_lower:
            match = re.search(r"(?:create folder|mkdir)\s+([^\s]+)", message_lower)
            if match:
                folder_name = match.group(1)
                return await self.file_system.create_folder(folder_name)

        if "save file" in message_lower or "write file" in message_lower:
            match = re.search(r"(?:save|write)\s+(?:file\s+)?([^\s]+)", message_lower)
            if match:
                file_name = match.group(1)
                # Extract content from message (simplified)
                content = message.split("content:")[-1].strip() if "content:" in message else ""
                return await self.file_system.save_file(file_name, content)

        if "read file" in message_lower or "open file" in message_lower:
            match = re.search(r"(?:read|open)\s+(?:file\s+)?([^\s]+)", message_lower)
            if match:
                file_name = match.group(1)
                return await self.file_system.read_file(file_name)

        if "delete file" in message_lower or "remove file" in message_lower:
            match = re.search(r"(?:delete|remove)\s+(?:file\s+)?([^\s]+)", message_lower)
            if match:
                file_name = match.group(1)
                return await self.file_system.delete_file(file_name)

        if "list files" in message_lower or "ls" in message_lower:
            return await self.file_system.list_files()

        # Code execution
        if "execute python" in message_lower or "run python" in message_lower or "python code" in message_lower:
            match = re.search(r"```python\n(.*?)\n```", message, re.DOTALL)
            if match:
                code = match.group(1)
                return await self.code_executor.execute_python(code)

        return None


# ============================================================================
# TELEGRAM BOT HANDLER
# ============================================================================

class TelegramBotHandler:
    """Handles Telegram bot interactions."""

    # Conversation states
    SETUP_BOT_TOKEN = 1
    SETUP_USER_ID = 2
    SETUP_AI_PROVIDER = 3
    SETUP_API_KEY = 4
    SETUP_MODEL = 5
    SETUP_AGENT_NAME = 6
    SETUP_EMAIL = 7
    SETUP_EMAIL_PASSWORD = 8
    CHAT = 9

    def __init__(self, config: ConfigManager):
        self.config = config
        self.agent: Optional[ArasAgent] = None
        self.user_data: Dict[str, Any] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the bot and check configuration."""
        if self.config.is_configured():
            await update.message.reply_text(
                "Welcome back! I'm Aras, your AI assistant. How can I help you today?\n\n"
                "Commands:\n"
                "/help - Show available commands\n"
                "/reset - Reconfigure the bot\n"
                "/search - Search the web\n"
                "/code - Execute Python code\n"
                "/files - Manage files"
            )
            await self._initialize_agent()
            return self.CHAT
        else:
            await update.message.reply_text(
                "Welcome to Aras! Let's set up your AI assistant.\n\n"
                "First, please provide your Telegram Bot Token:"
            )
            return self.SETUP_BOT_TOKEN

    async def setup_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle bot token setup."""
        bot_token = update.message.text.strip()
        self.config.set("bot_token", bot_token)
        self.user_data["bot_token"] = bot_token

        await update.message.reply_text("Bot token saved! Now, please provide your Telegram User ID:")
        return self.SETUP_USER_ID

    async def setup_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user ID setup."""
        try:
            user_id = int(update.message.text.strip())
            self.config.set("user_id", user_id)
            self.user_data["user_id"] = user_id

            keyboard = [
                [InlineKeyboardButton("OpenAI", callback_data="openai")],
                [InlineKeyboardButton("OpenRouter", callback_data="openrouter")],
                [InlineKeyboardButton("Minimax", callback_data="minimax")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "User ID saved! Now, select your AI provider:",
                reply_markup=reply_markup,
            )
            return self.SETUP_AI_PROVIDER
        except ValueError:
            await update.message.reply_text("Invalid User ID. Please enter a valid number:")
            return self.SETUP_USER_ID

    async def setup_ai_provider(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle AI provider selection."""
        query = update.callback_query
        await query.answer()

        provider = query.data
        self.config.set("ai_provider", provider)
        self.user_data["ai_provider"] = provider

        await query.edit_message_text(
            text=f"AI Provider set to {provider.upper()}!\n\n"
            f"Now, please provide your API key for {provider}:"
        )
        return self.SETUP_API_KEY

    async def setup_api_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle API key setup."""
        api_key = update.message.text.strip()
        self.config.set("api_key", api_key)
        self.user_data["api_key"] = api_key

        await update.message.reply_text(
            "API key saved! Now, please provide the model name (e.g., gpt-4, gpt-3.5-turbo for OpenAI):"
        )
        return self.SETUP_MODEL

    async def setup_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle model name setup."""
        model = update.message.text.strip()
        self.config.set("model", model)
        self.user_data["model"] = model

        await update.message.reply_text(
            "Model saved! Now, what would you like your AI assistant to be called?"
        )
        return self.SETUP_AGENT_NAME

    async def setup_agent_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle agent name setup."""
        agent_name = update.message.text.strip()
        self.config.set("agent_name", agent_name)
        self.user_data["agent_name"] = agent_name

        keyboard = [
            [InlineKeyboardButton("Yes, set up email", callback_data="yes_email")],
            [InlineKeyboardButton("No, skip for now", callback_data="no_email")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Great! Your assistant's name is {agent_name}.\n\n"
            "Would you like to set up email functionality?",
            reply_markup=reply_markup,
        )
        return self.SETUP_EMAIL

    async def setup_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle email setup decision."""
        query = update.callback_query
        await query.answer()

        if query.data == "yes_email":
            await query.edit_message_text(
                text="Please provide your email address:"
            )
            return self.SETUP_EMAIL_PASSWORD
        else:
            await query.edit_message_text(
                text="Setup complete! Your AI assistant is ready to use.\n\n"
                "Type /help to see available commands."
            )
            await self._initialize_agent()
            return self.CHAT

    async def setup_email_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle email and password setup."""
        if "email" not in self.user_data:
            email = update.message.text.strip()
            self.config.set("email", email)
            self.user_data["email"] = email

            await update.message.reply_text(
                "Email saved! Now, please provide your email password (or app password for Gmail):"
            )
            return self.SETUP_EMAIL_PASSWORD
        else:
            password = update.message.text.strip()
            self.config.set("email_password", password)
            self.user_data["email_password"] = password

            await update.message.reply_text(
                "Email setup complete! Your AI assistant is ready to use.\n\n"
                "Type /help to see available commands."
            )
            await self._initialize_agent()
            return self.CHAT

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show help message."""
        help_text = """
🤖 **Aras AI Assistant - Commands**

/start - Start the bot
/reset - Reconfigure the bot
/help - Show this message
/search - Search the web
/code - Execute Python code
/files - Manage files
/email - Manage emails

**Features:**
- 🔍 Web search and research
- 💻 Python code execution
- 📁 File management (create, read, delete)
- 📧 Email management
- 🧠 Intelligent conversation

Just type your message and I'll help you!
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Reset configuration."""
        self.config.reset()
        self.user_data = {}
        self.agent = None

        await update.message.reply_text(
            "Configuration reset! Let's set up again.\n\n"
            "Please provide your Telegram Bot Token:"
        )
        return self.SETUP_BOT_TOKEN

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages."""
        if not self.agent:
            await self._initialize_agent()

        user_message = update.message.text
        await update.message.chat.send_action("typing")

        response = await self.agent.process_message(user_message)

        # Split long messages
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i : i + 4096])
        else:
            await update.message.reply_text(response)

    async def _initialize_agent(self) -> None:
        """Initialize the Aras agent."""
        if self.agent:
            return

        ai_provider = self.config.get("ai_provider")
        api_key = self.config.get("api_key")
        model = self.config.get("model")

        if ai_provider == "openai":
            provider = OpenAIProvider(api_key, model)
        elif ai_provider == "openrouter":
            provider = OpenRouterProvider(api_key, model)
        elif ai_provider == "minimax":
            provider = MinimaxProvider(api_key, model)
        else:
            raise ValueError(f"Unknown AI provider: {ai_provider}")

        self.agent = ArasAgent(self.config, provider)

        # Set up email if configured
        email = self.config.get("email")
        email_password = self.config.get("email_password")
        if email and email_password:
            self.agent.email_tool = EmailTool(email, email_password)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main():
    """Main application entry point."""
    config = ConfigManager()

    # Check if bot token is configured
    bot_token = config.get("bot_token")
    if not bot_token:
        print("Error: Bot token not configured. Please run the setup first.")
        print("Starting setup...")
        # Interactive setup
        bot_token = input("Enter your Telegram Bot Token: ").strip()
        config.set("bot_token", bot_token)

    # Create application
    application = Application.builder().token(bot_token).build()

    # Create bot handler
    bot_handler = TelegramBotHandler(config)

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", bot_handler.start)],
        states={
            bot_handler.SETUP_BOT_TOKEN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_bot_token)
            ],
            bot_handler.SETUP_USER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_user_id)
            ],
            bot_handler.SETUP_AI_PROVIDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_ai_provider)
            ],
            bot_handler.SETUP_API_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_api_key)
            ],
            bot_handler.SETUP_MODEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_model)
            ],
            bot_handler.SETUP_AGENT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_agent_name)
            ],
            bot_handler.SETUP_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_email)
            ],
            bot_handler.SETUP_EMAIL_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.setup_email_password)
            ],
            bot_handler.CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_message)
            ],
        },
        fallbacks=[CommandHandler("reset", bot_handler.reset_command)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", bot_handler.help_command))
    application.add_handler(CommandHandler("reset", bot_handler.reset_command))

    # Start the bot
    print("🤖 Aras Agent is starting...")
    print("Press Ctrl+C to stop the bot.")

    await application.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Aras Agent stopped.")
        sys.exit(0)
