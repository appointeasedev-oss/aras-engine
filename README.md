# Aras AI Agent

Aras is a comprehensive, single-file AI agent for Telegram, designed to be a versatile and intelligent assistant. It supports multiple AI providers and comes equipped with a suite of tools for web research, coding, file management, and email operations.

## Features

-   **Single-file Application**: The entire agent logic is contained within `aras.py`.
-   **Multi-provider Support**: Integrates with OpenAI, OpenRouter, and Minimax.
-   **Termux Compatible**: Optimized for running on mobile devices via Termux.
-   **Interactive Setup**: Easy first-time configuration via Telegram.
-   **Tool Suite**:
    -   🔍 **Web Research**: Search the web and retrieve information.
    -   💻 **Code Execution**: Write and run Python code.
    -   📁 **File Management**: Create, read, delete, and list files and folders.
    -   📧 **Email Management**: Send and read emails (requires SMTP/IMAP setup).
-   **Human-like Personality**: Customizable agent name and persona.

## Installation

### Standard Environment

1.  Clone the repository:
    ```bash
    git clone https://github.com/appointeasedev-oss/aras-engine.git
    cd aras-engine
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the agent:
    ```bash
    python aras.py
    ```

### Termux Environment

1.  Install Python and Git:
    ```bash
    pkg install python git
    ```
2.  Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/appointeasedev-oss/aras-engine.git
    cd aras-engine
    pip install -r requirements.txt
    ```
3.  Run the agent:
    ```bash
    python aras.py
    ```

## Usage

On the first run, the agent will guide you through the setup process on Telegram. You will need:
-   A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
-   Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))
-   An API key from your chosen AI provider (OpenAI, OpenRouter, or Minimax)

### Commands

-   `/start`: Initiates the bot and setup process.
-   `/help`: Displays available commands and features.
-   `/reset`: Resets the configuration and restarts the setup.

## License

MIT License
