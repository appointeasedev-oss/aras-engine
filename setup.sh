#!/bin/bash

# Aras Engine - Termux Installation Script

echo "--- Aras Engine Setup ---"

# Check if running in Termux
if [ -d "/data/data/com.termux/files/home" ]; then
    echo "Detected Termux environment."
    # Install dependencies
    pkg update && pkg upgrade -y
    pkg install python git nodejs -y
else
    echo "Not running in Termux. Proceeding with standard installation."
fi

# Install Python requirements
pip install -r requirements.txt

# Create a symlink to the aras command in /usr/local/bin or ~/bin
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"
ln -sf "$(pwd)/bin/aras" "$BIN_DIR/aras"

# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Adding $BIN_DIR to PATH in .bashrc"
    echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
    source "$HOME/.bashrc"
fi

echo "Installation complete! You can now run 'aras' from your terminal."
echo "Note: You may need to restart your terminal or run 'source ~/.bashrc' to use the 'aras' command."
