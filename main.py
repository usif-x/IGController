from telebot import TeleBot, types # Make sure types is imported
import config
import time # Import time for sleep
import os # Import os for path checks
from src.helpers.ig.login import InstagramHelper
from src.handlers.bot.start_handler import StartHandler
from src.handlers.bot.callback_handler import CallbackHandler
from src.handlers.bot.ai_handler import AIHandler

# Initialize Instagram helper
ig_helper = InstagramHelper()

# Initialize Telegram bot
bot = TeleBot(config.bot_token)

# Initialize handlers
start_handler = StartHandler(bot, ig_helper)
callback_handler = CallbackHandler(bot, ig_helper, start_handler) # Pass start_handler
ai_handler = AIHandler(bot)


def is_admin(data):
    return str(data.from_user.id) == config.admin_id

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if not is_admin(message):
        bot.reply_to(message, "⛔ This bot is not available for you")
        return

    # Check if it's a reply to one of our prompts (for editing)
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
         # Check if it's a reply related to profile editing
         if callback_handler.user_states.get(message.chat.id, {}).get("action", "").startswith("edit_"):
              callback_handler.handle_edit_reply(message)
              return # Stop further processing if it was an edit reply

         # Check if it's a reply related to AI (if you implement /ai prompt replies)
         # elif ai_handler.is_ai_reply(message): # You'd need to implement this check
         #     ai_handler.handle_ai_reply(message)
         #     return

         # Check if it's a reply related to login
         elif message.reply_to_message.text == "🔑 Please enter your Instagram username:":
             callback_handler.process_username_step(message)
             return
         elif message.reply_to_message.text == "🔒 Please enter your Instagram password:":
             callback_handler.process_password_step(message)
             return


    if message.text.startswith('/'):
        handle_commands(message)
    # elif message.content_type == 'text': # Handle non-command text if needed
    #     # Example: Treat non-command text as an AI query if desired
    #     # ai_handler.handle_ai_message(message)
    #     bot.reply_to(message, "❌ Unrecognized action. Use /help to see commands.")
    else:
         # Handle other content types if necessary
         bot.reply_to(message, "❌ Unrecognized action or content type.")


def handle_commands(message):
    if message.text == '/start':
        start_handler.handle_start_command(message)
    elif message.text == '/help':
        start_handler.handle_help_command(message)
    elif message.text == '/account':
        start_handler.handle_account_info(message)
    elif message.text.startswith('/ai'):
        # Check if there's text after the /ai command
        if len(message.text) > 3 and message.text[3] == ' ':
            # Extract the query after "/ai "
            query = message.text[4:].strip()
            if query:
                # Modify message text to be only the query for the handler
                message.text = query
                ai_handler.handle_ai_message(message)
            else:
                bot.reply_to(message, "Please provide a question after /ai")
        else:
            # Just /ai command without text
            ai_handler.handle_ai_command(message) # This prompts the user
    elif message.text.startswith('/ask '):
        # Handle direct AI queries like "/ask What is Instagram?"
        query = message.text[5:].strip()
        if query:
            # Modify message text to be only the query for the handler
            message.text = query
            ai_handler.handle_ai_message(message)
        else:
            bot.reply_to(message, "Please provide a question after /ask")
    elif message.text == '/logout':
        # Add logout command
        try:
            logged_out = ig_helper.client.logout()
            if logged_out and os.path.exists(ig_helper.session_file):
                os.remove(ig_helper.session_file)
                bot.reply_to(message, "✅ Successfully logged out and session removed.")
            elif logged_out:
                 bot.reply_to(message, "✅ Successfully logged out (no session file found).")
            else:
                 bot.reply_to(message, "ℹ️ Logout function executed, but status unclear (might have already been logged out).")
        except Exception as e:
            bot.reply_to(message, f"❌ Error during logout: {str(e)}")
    else:
        bot.reply_to(message, "❌ Unrecognized command. Use /help.")


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
    
    # Start the bot with connection resilience
    while True:
        try:
            bot.infinity_polling()
        except (ConnectionResetError, ConnectionError) as e:
            print(f"Connection error: {str(e)}. Reconnecting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Critical error: {str(e)}")
            break