import telebot
from aras.config import load_config
from aras.agent.engine import ArasAgent

def start_bot():
    config = load_config()
    token = config.get("telegram_bot_token")
    allowed_users = config.get("allowed_user_ids", [])
    
    if not token:
        print("Error: Telegram bot token not configured. Run 'aras configure' to add it.")
        return

    bot = telebot.TeleBot(token)
    agent = ArasAgent()

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        if allowed_users and message.from_user.id not in allowed_users:
            bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            answer = agent.process_query(message.text)
            bot.reply_to(message, answer)
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

    print(f"Starting Telegram bot... (Allowed users: {allowed_users})")
    bot.infinity_polling()
