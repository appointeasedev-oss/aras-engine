# Aras Engine

Aras is a Termux-compatible CLI agent designed to run on Android without root. It provides a multi-call AI agent capable of generating code and managing a workspace.

## Features

- **Multi-call AI Agent**: Aras can think, reason, and perform multiple API calls to solve complex tasks.
- **Workspace Management**: Aras can create React apps or pure HTML/CSS/JS apps in its workspace.
- **Telegram Bot Integration**: Chat with Aras from your Telegram bot.
- **Local Terminal Chat**: Chat with Aras directly from your terminal.
- **OpenRouter Support**: Multi-key and multi-model support for reliable AI interactions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/appointeasedev-oss/aras-engine
   ```
2. Run the setup script:
   ```bash
   cd aras-engine && bash setup.sh
   ```
3. Restart your terminal or run `source ~/.bashrc`.

## Usage

- `aras setup`: Setup device local storage and workspace folder.
- `aras configure`: Configure Telegram bot ID and allowed user IDs.
- `aras models`: Manage OpenRouter API keys and models.
- `aras serve`: Start the Telegram bot.
- `aras serve local`: Start a terminal-based chat.

## Workspace

The default workspace is located at `~/aras-workspace`. You can change this in the configuration.

## License

MIT
