import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration variables
SESSION = os.getenv("SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_HASH = os.getenv("API_HASH")
API_ID = int(os.getenv("API_ID"))
CHANNEL_WHITELIST = list(map(int, os.getenv("CHANNEL_WHITELIST", "").split(',')))
USER_WHITELIST = list(map(int, os.getenv("USER_WHITELIST", "").split(',')))

