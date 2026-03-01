import argparse
import sys
from aras.config import configure_settings, manage_models
from aras.setup import setup_workspace
from aras.bot.telegram import start_bot
from aras.agent.engine import start_local_chat

def main():
    parser = argparse.ArgumentParser(description="Aras Engine - Termux AI Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # aras serve
    serve_parser = subparsers.add_parser("serve", help="Start the Telegram bot or local chat")
    serve_parser.add_argument("mode", nargs="?", choices=["local"], help="Start in local terminal mode")

    # aras configure
    subparsers.add_parser("configure", help="Configure Telegram bot ID and allowed user IDs")

    # aras setup
    subparsers.add_parser("setup", help="Setup device local storage and workspace folder")

    # aras models
    subparsers.add_parser("models", help="Manage OpenRouter API keys and models")

    args = parser.parse_args()

    if args.command == "serve":
        if args.mode == "local":
            start_local_chat()
        else:
            start_bot()
    elif args.command == "configure":
        configure_settings()
    elif args.command == "setup":
        setup_workspace()
    elif args.command == "models":
        manage_models()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
