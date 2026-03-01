# Aras Agent Design Document

## 1. Introduction

This document outlines the design and architecture for the Aras agent, a single-file Python Telegram bot. The agent aims to replicate the core functionalities of OpenClaw, providing a highly capable and customizable AI assistant that can run efficiently on environments like Termux.

## 2. Core Requirements

*   **Single-file Application**: All code will reside in `aras.py`.
*   **Dependency Management**: A `requirements.txt` file will list all necessary Python packages.
*   **Termux Compatibility**: The agent must be runnable on Termux, implying minimal system-level dependencies and efficient resource usage.
*   **Telegram Bot Integration**: Full interaction via Telegram, including message handling and command processing.
*   **First-time Setup & Configuration**: 
    *   Interactive setup for Telegram Bot Token, User ID, AI model provider (OpenAI, OpenRouter, Minimax), API keys, and agent's name.
    *   Configuration persistence (e.g., JSON file).
    *   `/reset` command to re-run the setup.
*   **AI Core & Personality**: 
    *   Support for multiple LLM providers.
    *   Context management for maintaining conversation flow and agent personality.
    *   Agent should act like a human, developing its own 
sole and personality.
*   Mini-OpenClaw capabilities: web research, coding, mail management, file operations (create, delete, new folder, save file).

## 3. Technical Design

### 3.1. File Structure

```
/home/ubuntu/aras-engine/
├── aras.py
├── requirements.txt
└── config.json (for persistent configuration)
```

### 3.2. Core Components

*   **Telegram Bot Handler**: Manages incoming messages and dispatches commands.
*   **Configuration Manager**: Handles loading, saving, and updating `config.json`.
*   **AI Provider Interface**: Abstract layer for interacting with different LLM APIs (OpenAI, OpenRouter, Minimax).
*   **Agent Core**: Manages conversation context, personality, and tool invocation.
*   **Tool Executor**: Executes various tools (web search, file system operations, code interpreter, email client).

### 3.3. Data Persistence

*   **`config.json`**: Stores bot token, user ID, AI provider details, API keys, agent name, and personality traits.
*   **Conversation History**: Managed in-memory or optionally persisted for longer-term context.

## 4. Development Plan

1.  **Setup**: Initialize the project structure and `requirements.txt`.
2.  **Configuration**: Implement the `config.json` management and first-time setup flow.
3.  **Telegram Integration**: Set up basic message handling and command processing.
4.  **AI Integration**: Develop the abstract AI provider interface and integrate with selected LLMs.
5.  **Agent Core**: Implement context management and personality features.
6.  **Tooling**: Integrate web search, file system, coding, and email tools.
7.  **Testing & Refinement**: Ensure Termux compatibility and overall stability.

## 5. Dependencies

*   `python-telegram-bot`
*   `openai` (for OpenAI and OpenRouter compatibility)
*   `requests` (for general API calls and web scraping)
*   `beautifulsoup4` (for web scraping)
*   `smtplib`, `imaplib` (for email functionality)
*   `minimax` (if a dedicated client exists, otherwise use `requests`)

## 6. Usage on Termux

1.  Install Python and pip.
2.  `pip install -r requirements.txt`
3.  `python aras.py`

## 7. Commands

*   `/start`: Initiates the bot and first-time setup if not configured.
*   `/reset`: Clears existing configuration and restarts the setup process.
*   `/help`: Displays available commands and agent capabilities.

## 8. Future Enhancements

*   Advanced natural language understanding for tool selection.
*   More sophisticated memory management.
*   Integration with other communication platforms.
