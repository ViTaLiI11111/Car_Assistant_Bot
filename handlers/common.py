from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import MANAGER_USERNAME

CHOOSING = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        ["Розрахунок вартості ремонту", "Калькулятор розмитнення"],
        ["📂 Моя історія", "💬 Зв'язатися з менеджером"]
    ]

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


async def contact_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Написати менеджеру", url=f"https://t.me/{MANAGER_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Натисніть кнопку нижче, щоб зв'язатися з нашим менеджером для консультації.",
        reply_markup=reply_markup
    )

    return await start(update, context)

async def handle_unsupported_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Вибачте, я не обробляю голосові повідомлення чи відео-кружечки. "
        "Будь ласка, використовуйте текстові команди або надсилайте фото."
    )