import time
import math
from telebot import types # Make sure types is imported if not already globally
from telebot.apihelper import ApiTelegramException # Import specific exception
from src.plugins.openrouter import OpenRouterAPI # Assuming correct path

# --- Constants ---
TELEGRAM_MAX_MSG_LENGTH = 4096
# Leave some buffer for "... (continued)" or other markers
SAFE_EDIT_LENGTH = TELEGRAM_MAX_MSG_LENGTH - 50
# How often to attempt an edit (seconds)
EDIT_INTERVAL = 1.5

class AIHandler:
    """
    Handler for AI-related commands and interactions
    """

    def __init__(self, bot):
        self.bot = bot
        self.ai = OpenRouterAPI() # Assuming OpenRouterAPI is correctly implemented for streaming

    def handle_ai_command(self, message):
        """Handle the /ai command to start AI interaction"""
        markup = types.ForceReply(selective=True)
        self.bot.send_message(
            message.chat.id,
            "💬 What would you like to ask the AI?",
            reply_markup=markup
        )

    def _send_large_text(self, chat_id, text, **kwargs):
        """Helper function to send text, splitting if needed."""
        if len(text) <= TELEGRAM_MAX_MSG_LENGTH:
            try:
                self.bot.send_message(chat_id, text, **kwargs)
            except ApiTelegramException as e:
                if "parse error" in str(e).lower():
                    print(f"Markdown parse error on send, sending plain. Error: {e}")
                    kwargs.pop('parse_mode', None) # Remove parse_mode
                    self.bot.send_message(chat_id, text, **kwargs)
                else:
                    print(f"Error sending message chunk: {e}") # Log other errors
        else:
            # Split the text
            num_chunks = math.ceil(len(text) / TELEGRAM_MAX_MSG_LENGTH)
            for i in range(num_chunks):
                start = i * TELEGRAM_MAX_MSG_LENGTH
                end = (i + 1) * TELEGRAM_MAX_MSG_LENGTH
                chunk = text[start:end]
                print(f"Sending chunk {i+1}/{num_chunks} (length {len(chunk)})")
                # Attempt to send chunk with original kwargs (e.g., parse_mode)
                try:
                    self.bot.send_message(chat_id, chunk, **kwargs)
                except ApiTelegramException as e:
                     if "parse error" in str(e).lower():
                        print(f"Markdown parse error on chunk {i+1}, sending plain. Error: {e}")
                        kwargs_plain = kwargs.copy()
                        kwargs_plain.pop('parse_mode', None)
                        self.bot.send_message(chat_id, chunk, **kwargs_plain)
                     else:
                        print(f"Error sending message chunk {i+1}: {e}")
                time.sleep(0.5) # Small delay between chunks


    def handle_ai_message(self, message):
        """Process a message as an AI query with streaming and length handling"""
        self.bot.send_chat_action(message.chat.id, 'typing')
        prompt = message.text
        full_response = ""
        message_id = None
        last_edit_time = 0
        can_edit = True # Flag to control editing

        try:
            # Send initial placeholder message
            msg = self.bot.send_message(message.chat.id, "🔄 Thinking...", parse_mode=None)
            message_id = msg.message_id

            # Stream responses
            for chunk in self.ai.get_text_response(prompt): # Assuming this yields strings
                if "Error:" in chunk: # Handle errors yielded from the API class
                    full_response = chunk # Store the error message
                    can_edit = False # Stop trying to edit if API yielded error
                    break # Stop processing chunks

                if chunk: # Process non-empty, non-error chunks
                    full_response += chunk
                    current_time = time.time()

                    # Check if we should attempt an edit
                    if can_edit and (current_time - last_edit_time > EDIT_INTERVAL):
                        # Construct text with streaming indicator
                        text_to_edit = full_response + "▌"

                        # Check length BEFORE trying to edit
                        if len(text_to_edit) < SAFE_EDIT_LENGTH:
                            try:
                                self.bot.edit_message_text(
                                    text=text_to_edit,
                                    chat_id=message.chat.id,
                                    message_id=message_id,
                                    parse_mode=None # IMPORTANT: No Markdown for intermediate edits
                                )
                                last_edit_time = current_time
                            except ApiTelegramException as edit_error:
                                error_str = str(edit_error).lower()
                                if "message is not modified" in error_str:
                                    pass # Ignore harmless error
                                elif "too many requests" in error_str:
                                    print(f"Rate limit hit during edit: {edit_error}")
                                    # Slow down editing if rate limited
                                    last_edit_time = current_time + EDIT_INTERVAL
                                else:
                                    # Other errors might mean we can't edit anymore
                                    print(f"Edit error (will stop editing): {edit_error}")
                                    can_edit = False
                        else:
                            # Text is too long for further edits, stop trying
                            print(f"Approaching message limit (len={len(full_response)}), stopping intermediate edits.")
                            can_edit = False
                            # Optional: Do one last edit to show it's still working but hit limit
                            try:
                                final_edit_text = full_response[:SAFE_EDIT_LENGTH - 20] + "... (processing)"
                                self.bot.edit_message_text(
                                     text=final_edit_text,
                                     chat_id=message.chat.id, message_id=message_id, parse_mode=None
                                )
                            except Exception:
                                pass # Ignore error on this optional final edit

            # --- Streaming Finished ---

            # Check if we have a valid message_id to finalize
            if not message_id:
                print("Error: No message_id to finalize.")
                # Send the response as a new message if initial send failed but we got response
                if full_response:
                     self._send_large_text(message.chat.id, full_response, parse_mode='Markdown')
                return

            # Now handle the final full_response
            if not full_response:
                # Edit the placeholder if no response was generated
                self.bot.edit_message_text(
                    text="⚠️ No response received from AI.",
                    chat_id=message.chat.id,
                    message_id=message_id,
                    parse_mode=None
                )
            elif len(full_response) <= TELEGRAM_MAX_MSG_LENGTH:
                # Final response fits in one message: Edit the original message
                try:
                    # Try final edit with Markdown
                    self.bot.edit_message_text(
                        text=full_response,
                        chat_id=message.chat.id,
                        message_id=message_id,
                        parse_mode='Markdown'
                    )
                except ApiTelegramException as final_edit_error:
                    # If Markdown fails, edit with plain text
                    error_str = str(final_edit_error).lower()
                    if "parse error" in error_str or "can't parse entities" in error_str:
                        print(f"Final Markdown edit failed, falling back to plain text. Error: {final_edit_error}")
                        try:
                            self.bot.edit_message_text(
                                text=full_response,
                                chat_id=message.chat.id,
                                message_id=message_id,
                                parse_mode=None # Fallback
                            )
                        except Exception as fallback_edit_error:
                             print(f"Fallback plain text edit failed: {fallback_edit_error}")
                    else:
                        # Log other potential errors during final edit
                        print(f"Final edit error: {final_edit_error}")

            else:
                # Final response is TOO LONG: Edit placeholder & send new messages
                print(f"Final response length ({len(full_response)}) exceeds limit. Sending in multiple messages.")
                try:
                    # Edit the original message to indicate completion
                    self.bot.edit_message_text(
                        text="✅ Response complete (sent below):",
                        chat_id=message.chat.id,
                        message_id=message_id,
                        parse_mode=None
                    )
                except Exception as final_placeholder_edit_error:
                     print(f"Could not edit final placeholder: {final_placeholder_edit_error}")

                # Send the full response split into chunks as NEW messages
                self._send_large_text(message.chat.id, full_response, parse_mode='Markdown')


        except Exception as e:
            # General error handling for the whole process
            print(f"Catastrophic error in handle_ai_message: {str(e)}")
            error_message = "❌ An unexpected error occurred while processing your request."
            if message_id:
                try:
                    self.bot.edit_message_text(text=error_message, chat_id=message.chat.id, message_id=message_id, parse_mode=None)
                except Exception:
                     # If editing fails, try sending a new message
                     self.bot.send_message(message.chat.id, error_message)
            else:
                 self.bot.send_message(message.chat.id, error_message)