import os
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN.")