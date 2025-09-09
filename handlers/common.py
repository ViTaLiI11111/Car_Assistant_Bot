from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

CHOOSING = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Розрахунок вартості ремонту", "Калькулятор розмитнення"]]

    await update.message.reply_text(
        "Вітаю! Оберіть одну з опцій нижче:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        "Дію скасовано. Щоб почати знову, надішліть /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END