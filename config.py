from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
ig_username = os.getenv("IG_USERNAME")
ig_password = os.getenv("IG_PASSWORD")

# Telegram Configuration
admin_id = os.getenv("ADMIN_ID")
bot_token = os.getenv("BOT_TOKEN")

# OpenAI Configuration
openrouter_key = os.getenv("OPENROUTER_KEY")
openrouter_model = os.getenv("OPENROUTER_MODEL")

# Application Settings
debug = os.getenv("DEBUG")
log_level = os.getenv("LOG_LEVEL")
timeout = os.getenv("TIMEOUT")

# Other Settings
max_retries = os.getenv("MAX_RETRIES")
wait_between_requests = os.getenv("WAIT_BETWEEN_REQUESTS")
max_accounts = os.getenv("MAX_ACCOUNTS")
