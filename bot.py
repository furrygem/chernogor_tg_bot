import os
import logging
import random
import re
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

SESSIONS_DIR = os.path.join(os.getcwd(), 'sessions')
os.makedirs(SESSIONS_DIR, exist_ok=True)

session_path = os.path.join(SESSIONS_DIR, 'bot_session')
client = TelegramClient(session_path, API_ID, API_HASH)

QUOTES = [
    "Не сейчас, я отдыхаю",
    "Я отдыхаю",
]

ZAPOVEDI = [
    "Человек родился усталым и живет, чтобы отдохнуть",
    "Люби кровать свою, как себя самого",
    "Отдохни днем, чтобы ночью мог поспать",
    "Не трудись - работа убивает",
    "Если видишь - что кто-то отдыхает - помоги ему",
    "Делай меньше и только то, что можешь, а то, что не можешь, передай другим",
    "В тени деревьев - спасение, от отдыха еще никто не умирал",
    "Работа приносит болезни - не умри молодым",
    "Когда захочешь поработать, сядь, подожди - увидишь, это пройдет",
    "Когда увидишь где едят и пьют - присоединяйся, а когда увидишь где работают - уходи, чтобы не мешать",
]

TRIGGER_WORDS = [
    r'\bраб\w*',
    r'\bработа\w*',
    r'\bработать\w*',
]

def get_random_message():
    """Random message getter function"""
    choice = random.randint(0, 2)
    if choice == 0:
        return random.choice(QUOTES)
    elif choice == 1:
        return random.choice(ZAPOVEDI)
    else:
        return f"{random.choice(QUOTES)}. Мой тебе совет: {random.choice(ZAPOVEDI)}"

def contains_work_words(text):
    if not text:
        return False
    text_lower = text.lower()
    for pattern in TRIGGER_WORDS:
        if re.search(pattern, text_lower):
            return True
    return False

@client.on(events.NewMessage(pattern=r'^@\w+'))
async def handle_ping(event):
    """Handle when the bot is pinged with @username"""
    try:
        if event.message.mentioned:
            message = get_random_message()
            await event.reply(message)
            logger.info(f"Replied to ping from {event.sender_id}")
    except Exception as e:
        logger.error(f"Error handling ping: {e}")

@client.on(events.NewMessage())
async def handle_work_words(event):
    try:
        if event.message.reply_to:
            return

        if event.message.mentioned:
            return

        message_text = event.message.text
        if message_text and contains_work_words(message_text):
            response = random.choice(ZAPOVEDI)
            await event.reply(response)
            logger.info(f"Replied to work-related message from {event.sender_id}: '{message_text[:50]}...'")
    except Exception as e:
        logger.error(f"Error handling work words: {e}")

@client.on(events.NewMessage())
async def handle_reply(event):
    """Handle replies"""
    try:
        if event.message.reply_to:
            replied_message = await event.get_reply_message()
            
            if replied_message and replied_message.sender_id == (await client.get_me()).id:
                message = get_random_message()
                await event.reply(message)
                logger.info(f"Replied to reply from {event.sender_id}")
    except Exception as e:
        logger.error(f"Error handling reply: {e}")

async def main():
    logger.info("Starting bot...")
    
    await client.start(bot_token=BOT_TOKEN)
    
    logger.info("Bot is running. Press Ctrl+C to stop.")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}") 