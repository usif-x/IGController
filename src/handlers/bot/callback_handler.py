class CallbackHandler:
    def __init__(self, bot, ig_helper, start_handler):
        self.bot = bot
        self.ig_helper = ig_helper
        self.start_handler = start_handler
    
    def handle_callback(self, call):
        if call.data == "check_login":
            status = self.ig_helper.check_status()
            self.bot.answer_callback_query(
                call.id, 
                "✅ Already logged in!" if status else "❌ Login required",
                show_alert=True
            )
        
        elif call.data == "instagram_login":
            success, message = self.ig_helper.login()
            self.bot.send_message(
                call.message.chat.id,
                f"{'✅' if success else '❌'} {message}"
            )
        
        elif call.data == "account_info":
            self.start_handler.handle_account_info(call.message)
        
        self.bot.answer_callback_query(call.id)