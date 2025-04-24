from telebot import TeleBot
import config
from src.helpers.ig.login import InstagramHelper
from src.handlers.bot.start_handler import StartHandler
from src.handlers.bot.callback_handler import CallbackHandler

# Initialize Instagram helper
ig_helper = InstagramHelper()

# Initialize Telegram bot
bot = TeleBot(config.bot_token)

# Initialize handlers
start_handler = StartHandler(bot, ig_helper)
callback_handler = CallbackHandler(bot, ig_helper, start_handler)

def is_admin(data):
    return str(data.from_user.id) == config.admin_id

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if not is_admin(message):
        bot.reply_to(message, "⛔ This bot is not available for you")
        return
    
    if message.text.startswith('/'):
        handle_commands(message)
    else:
        bot.reply_to(message, "❌ Unrecognized action")

def handle_commands(message):
    if message.text == '/start':
        start_handler.handle_start_command(message)
    elif message.text == '/help':
        start_handler.handle_help_command(message)
    elif message.text == '/account':
        start_handler.handle_account_info(message)
    elif message.text == '/logout':
        # Add logout command
        try:
            ig_helper.client.logout()
            if os.path.exists(ig_helper.session_file):
                os.remove(ig_helper.session_file)
            bot.reply_to(message, "✅ Successfully logged out")
        except Exception as e:
            bot.reply_to(message, f"❌ Error during logout: {str(e)}")
    else:
        bot.reply_to(message, "❌ Unrecognized command")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id, "Not authorized!", show_alert=True)
        return
    
    callback_handler.handle_callback(call)

if __name__ == '__main__':
    # Try to login at startup using saved session
    success, message = ig_helper.login()
    print(f"Login status: {success}, Message: {message}")
    
    # Start the bot
    bot.infinity_polling()