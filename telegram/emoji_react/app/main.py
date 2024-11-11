import sys
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

import asyncio
import logging
import random
from config import API_ID, API_HASH, CHANNEL_WHITELIST, USER_WHITELIST, SESSION
from emoji_keywords import EMOJI_KEYWORDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():

    @events.register(events.NewMessage)
    async def handler(event):
        message_text = event.message.message.lower()
        if event.from_id:
            if event.from_id.user_id in USER_WHITELIST:
                if event.peer_id.channel_id in CHANNEL_WHITELIST:
                    message_text = event.message.message.lower()
                    for keyword, emojis in EMOJI_KEYWORDS.items():
                        if keyword in message_text:
                            chosen_emojis = random.sample(emojis, 2)
                            for emoji in chosen_emojis:
                                await add_reaction(event, emoji)
    
    client = TelegramClient(session=SESSION, api_id=API_ID, api_hash=API_HASH)
    async with client:
        await client.start()
        client.add_event_handler(handler)
        me = await client.get_me()
        username = me.username
        print(f"Hello Professor {username}. How about a nice game of chess?")
        print(f"Monitoring channels {CHANNEL_WHITELIST} for keywords {EMOJI_KEYWORDS.keys()} from users {USER_WHITELIST}")
            
        async def add_reaction(event, emoji):
            await client(SendReactionRequest(
                    peer=event.chat_id,
                    msg_id=event.message.id,
                    reaction=[ReactionEmoji(emoticon=emoji)]
                )
            )
            logger.info(f"Added reaction '{emoji}' to message {event.message.id} in chat {event.chat_id}")
        try:
            await client.run_until_disconnected()
        except KeyboardInterrupt:
            print(f"Goodbye Professor {username}")
            sys.exit(0)

asyncio.run(main())
