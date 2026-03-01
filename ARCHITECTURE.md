# Aras Engine Architecture

Aras is a Termux-compatible CLI agent designed to run on Android without root. It provides a multi-call AI agent capable of generating code and managing a workspace.

## Directory Structure

```text
aras-engine/
├── bin/
│   └── aras                # CLI entry point (shell script)
├── aras/
│   ├── __init__.py
│   ├── cli.py              # Command line argument parsing
│   ├── config.py           # Configuration management (Telegram, OpenRouter)
│   ├── setup.py            # Device and workspace setup logic
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── engine.py       # Main agent logic (multi-call, reasoning)
│   │   ├── llm.py          # OpenRouter client with multi-key/model support
│   │   └── memory.py       # Conversation and state memory
│   ├── bot/
│   │   ├── __init__.py
│   │   └── telegram.py     # Telegram bot implementation
│   ├── workspace/
│   │   ├── __init__.py
│   │   └── manager.py      # Workspace and file operations
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Common utility functions
├── setup.sh                # Installation script for Termux
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## Core Components

### 1. CLI Entry Point (`aras`)
A shell script that routes commands to the Python package.
- `aras serve`: Starts the Telegram bot.
- `aras serve local`: Starts a terminal-based chat.
- `aras configure`: Interactive setup for API keys and IDs.
- `aras setup`: Initializes the `aras-workspace` folder.
- `aras models`: Manages OpenRouter keys and models.

### 2. Configuration (`config.py`)
Stores settings in `~/.aras/config.json`.
- Telegram Bot Token
- Allowed User IDs
- OpenRouter API Keys (Multiple)
- Preferred Models (Multiple)

### 3. AI Agent (`agent/`)
- **Engine**: Implements a "Think-Act-Observe" loop.
- **LLM Client**: Handles failover between multiple OpenRouter keys and models.
- **Memory**: Persistent storage for chat history and agent state.

### 4. Workspace Manager (`workspace/`)
Manages the `aras-workspace` directory.
- Creates React apps or pure HTML/CSS/JS projects.
- Handles file reading/writing for the agent.

### 5. Telegram Bot (`bot/`)
Uses `python-telegram-bot` or `telebot` to provide a chat interface for the agent.

## Installation Flow
1. `git clone https://github.com/appointeasedev-oss/aras-engine`
2. `cd aras-engine && bash setup.sh`
3. `aras setup`
4. `aras configure`
5. `aras models`
6. `aras serve`
