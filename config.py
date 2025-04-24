from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
ig_username = os.getenv("IG_USERNAME")
ig_password = os.getenv("IG_PASSWORD")