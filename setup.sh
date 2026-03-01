#!/bin/bash

# Aras Engine - Advanced Termux Installation Script

echo "--- Aras Engine Advanced Setup ---"

# Check if running in Termux
if [ -d "/data/data/com.termux/files/home" ]; then
    echo "[*] Detected Termux environment."
    # Install dependencies
    pkg update && pkg upgrade -y
    pkg install python git nodejs-lts build-essential -y
    # Ensure storage access
    termux-setup-storage
else
    echo "[!] Not running in Termux. Proceeding with standard installation."
fi

# Install Python requirements
pip install -r requirements.txt

# Create a symlink to the aras command in /usr/local/bin or ~/bin
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"
ln -sf "$(pwd)/bin/aras" "$BIN_DIR/aras"

# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "[*] Adding $BIN_DIR to PATH in .bashrc"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
    source "$HOME/.bashrc"
fi

# Initialize workspace
mkdir -p "$HOME/aras-workspace"

echo "--- Installation Complete ---"
echo "1. Run 'source ~/.bashrc' or restart your terminal."
echo "2. Run 'aras setup' to initialize the workspace."
echo "3. Run 'aras models' to add your OpenRouter API keys."
echo "4. Run 'aras configure' to set up your Telegram bot."
echo "5. Run 'aras serve local' to start chatting with Aras!"
