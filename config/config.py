import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TOKEN_TG_VANEKO = os.getenv("TOKEN_TG_VANEKO")
APIKEY_GEMINI = os.getenv("APIKEY_GEMINI")

# Gemini configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-8b")

# Session configuration
SESSION_FILE = "database/sessions.json"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")