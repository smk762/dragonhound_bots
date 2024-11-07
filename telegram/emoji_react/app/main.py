import logging
from fastapi import FastAPI, Request, HTTPException
from requests.exceptions import RequestException
import requests
import random
from .config import BOT_TOKEN, CHANNEL_WHITELIST, USER_WHITELIST
from .emoji_keywords import EMOJI_KEYWORDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def set_message_reaction(chat_id, message_id, emoji, is_add=True):
    url = f"{TELEGRAM_API_URL}/setMessageReaction"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': emoji,
        'is_add': is_add
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Successfully reacted with {emoji} to message {message_id}")
    except RequestException as e:
        logger.error(f"Failed to react with {emoji} to message {message_id}: {e}")
        raise HTTPException(status_code=503, detail="Telegram API is currently unavailable")

# Example handle_message logging improvements
def handle_message(message):
    user_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    text = message.get("text", "")

    if chat_id not in CHANNEL_WHITELIST or (user_id and user_id not in USER_WHITELIST):
        logger.info(f"Ignoring message {message_id} from unlisted channel/user.")
        return

    for keyword, emojis in EMOJI_KEYWORDS.items():
        if keyword in text.lower():
            chosen_emojis = random.sample(emojis, 2)
            for emoji in chosen_emojis:
                set_message_reaction(chat_id, message_id, emoji, is_add=True)

@app.post(f"/emoji_webhook")
async def emoji_webhook(request: Request):
    data = await request.json()
    if 'message' in data:
        handle_message(data['message'])
    return {"status": "ok"}
