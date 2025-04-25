from telebot import types
import os

class CallbackHandler:
    def __init__(self, bot, ig_helper, start_handler):
        self.bot = bot
        self.ig_helper = ig_helper
        self.start_handler = start_handler
        # Store the next expected action for a user (e.g., waiting for new bio)
        self.user_states = {}

    def handle_callback(self, call):
        # Answer the callback query to remove the "loading" state on the button
        self.bot.answer_callback_query(call.id)

        # Extract callback data
        data = call.data

        if data == "login":
            # Prompt for username
            msg = self.bot.send_message(call.message.chat.id, "🔑 Please enter your Instagram username:")
            self.bot.register_next_step_handler(msg, self.process_username_step)
        elif data == "logout":
            try:
                self.ig_helper.client.logout()
                if os.path.exists(self.ig_helper.session_file):
                    os.remove(self.ig_helper.session_file)
                self.bot.edit_message_text("✅ Successfully logged out.", call.message.chat.id, call.message.message_id)
                # Optionally, show the start menu again
                self.start_handler.handle_start_command(call.message)
            except Exception as e:
                self.bot.send_message(call.message.chat.id, f"❌ Error during logout: {str(e)}")
        elif data == "account_info":
             # Call the account info handler from start_handler
             self.start_handler.handle_account_info(call.message)
        elif data == "edit_account":
            self.show_edit_options(call.message)
        elif data.startswith("edit_"):
            # Handle specific edit actions (e.g., edit_fullname, edit_biography)
            self.prompt_for_new_value(call.message, data)
        else:
            self.bot.send_message(call.message.chat.id, f"❓ Unknown callback action: {data}")

    def show_edit_options(self, message):
        """Shows buttons for available profile edit options."""
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📝 Edit Full Name", callback_data="edit_fullname"),
            types.InlineKeyboardButton("📄 Edit Biography", callback_data="edit_biography"),
            types.InlineKeyboardButton("🔗 Edit Website", callback_data="edit_website"),
            # Add more options if needed (e.g., email, phone)
            types.InlineKeyboardButton("🔙 Back to Account Info", callback_data="account_info")
        )
        self.bot.edit_message_text(
            "✏️ What would you like to edit?",
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=markup
        )

    def prompt_for_new_value(self, message, edit_action):
        """Prompts the user to enter the new value for the selected field."""
        field_name = edit_action.split('_')[1].capitalize() # e.g., "Fullname", "Biography"
        prompt_text = f"✏️ Please enter the new {field_name}:"

        # Use ForceReply to capture the user's next message
        markup = types.ForceReply(selective=True)
        sent_msg = self.bot.send_message(message.chat.id, prompt_text, reply_markup=markup)

        # Store the state: which field is being edited, and the original message_id to potentially delete later
        self.user_states[message.chat.id] = {
            "action": edit_action, # e.g., "edit_fullname"
            "original_message_id": message.message_id # ID of the message with edit buttons
        }

    def process_username_step(self, message):
       return 0
        # ... existing code ...

    def process_password_step(self, message):
        return 0
        # ... existing code ...

    # Add a method to handle the replies for edits
    def handle_edit_reply(self, message):
        """Handles the user's reply containing the new value for a profile field."""
        chat_id = message.chat.id
        if chat_id not in self.user_states or not self.user_states[chat_id].get("action", "").startswith("edit_"):
            # This message is not a reply to an edit prompt, ignore or handle differently
            return

        state = self.user_states.pop(chat_id) # Retrieve and clear state
        edit_action = state["action"]
        new_value = message.text.strip()

        # Determine which field to edit based on the action
        field_to_edit = edit_action.split('_')[1] # e.g., "fullname", "biography"

        try:
            # Call the helper function to perform the edit
            success = self.ig_helper.edit_profile(**{field_to_edit: new_value}) # Use keyword arguments

            if success:
                self.bot.send_message(chat_id, f"✅ Successfully updated your {field_to_edit.capitalize()}!")
                # Optionally, delete the prompt message and the user's reply
                try:
                    self.bot.delete_message(chat_id, message.message_id) # Delete user's reply
                    # self.bot.delete_message(chat_id, state["original_message_id"]) # Delete the message with buttons (optional)
                except Exception as del_err:
                    print(f"Could not delete messages: {del_err}")
                # Show updated account info
                self.start_handler.handle_account_info(message)
            else:
                self.bot.send_message(chat_id, f"❌ Failed to update your {field_to_edit.capitalize()}. Please try again.")

        except Exception as e:
            self.bot.send_message(chat_id, f"❌ An error occurred while editing profile: {str(e)}")
            print(f"Error editing profile: {e}")