import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_WHITELIST = list(map(int, os.getenv("CHANNEL_WHITELIST", "").split(',')))
USER_WHITELIST = list(map(int, os.getenv("USER_WHITELIST", "").split(',')))
