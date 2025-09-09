import random
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from .common import start

REPAIR_PHOTO = 1

async def repair_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Будь ласка, надішліть 1 або 2 фото вашого авто для попередньої оцінки вартості ремонту.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return REPAIR_PHOTO

#ЗАГЛУШКА
async def repair_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    estimated_cost = random.randint(5000, 45000)

    await update.message.reply_text(
        f"Дякую за фото!\n"
        f"Орієнтовна вартість ремонту складає: {estimated_cost} грн.\n\n"
        f"Для точного розрахунку, будь ласка, зверніться до нашого менеджера."
    )
    return await start(update, context)