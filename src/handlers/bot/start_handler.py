from telebot import types
from src.helpers.ig.login import InstagramHelper
import requests

class StartHandler:
    def __init__(self, bot, ig_helper):
        self.bot = bot
        self.ig_helper = ig_helper
    
    def handle_start_command(self, message):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔒 Check Login Status", callback_data="check_login"),
            types.InlineKeyboardButton("🔑 Login", callback_data="instagram_login"),
            types.InlineKeyboardButton("👤 Account Info", callback_data="account_info")
        )
        
        self.bot.send_message(message.chat.id, 
            "🤖 Instagram Controller Bot Ready!",
            reply_markup=markup
        )
    
    def handle_help_command(self, message):
        help_text = "Available Commands:\n/start - Initialize bot\n/help - Show this help\n/account - Show account info"
        self.bot.send_message(message.chat.id, help_text)
    
    def handle_account_info(self, message):
        try:
            # Get user info
            user_info = self.ig_helper.get_account_info()
            
            if not user_info:
                self.bot.send_message(message.chat.id, "❌ Not logged in or error retrieving account info")
                return
                
            user_id = user_info.pk
            username = user_info.username
            full_name = user_info.full_name
            biography = user_info.biography
            profile_pic_url = user_info.profile_pic_url
            
            # Format the account information
            account_text = f"📱 *Instagram Account Information*\n\n"
            account_text += f"👤 *Username:* {username}\n"
            account_text += f"📝 *Full Name:* {full_name}\n"
            account_text += f"🆔 *User ID:* {user_id}\n"
            account_text += f"📄 *Biography:* {biography}\n"
            
            # Send profile picture if available
            if profile_pic_url:
                try:
                    # Download the image first
                    response = requests.get(profile_pic_url)
                    if response.status_code == 200:
                        # Send the image bytes to Telegram
                        self.bot.send_photo(message.chat.id, response.content, caption=account_text, parse_mode="Markdown")
                    else:
                        # Fallback to text-only if image download fails
                        self.bot.send_message(message.chat.id, account_text, parse_mode="Markdown")
                except Exception as img_error:
                    print(f"Error downloading profile image: {str(img_error)}")
                    self.bot.send_message(message.chat.id, account_text, parse_mode="Markdown")
            else:
                self.bot.send_message(message.chat.id, account_text, parse_mode="Markdown")
                
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Error retrieving account info: {str(e)}")