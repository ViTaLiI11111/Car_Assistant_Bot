import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не знайдено TELEGRAM_BOT_TOKEN. Перевірте ваш .env файл.")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Не знайдено GOOGLE_API_KEY. Перевірте ваш .env файл.")