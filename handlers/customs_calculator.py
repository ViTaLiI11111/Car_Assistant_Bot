import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from .common import start

logger = logging.getLogger(__name__)

(ASK_PRICE, ASK_ENGINE, ASK_AGE) = range(2, 5)

async def customs_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Розпочнемо розрахунок.\n"
        "Введіть вартість авто в євро (€):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_PRICE


async def ask_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price = float(update.message.text.strip())
        context.user_data['price'] = price
        await update.message.reply_text("Тепер введіть об'єм двигуна (в кубічних сантиметрах, наприклад, 1998):")
        return ASK_ENGINE
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть числове значення для вартості.")
        return ASK_PRICE


async def ask_engine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        engine_size = int(update.message.text.strip())
        context.user_data['engine_size'] = engine_size
        await update.message.reply_text("Введіть повний вік автомобіля (в роках):")
        return ASK_AGE
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть ціле число для об'єму двигуна.")
        return ASK_ENGINE


async def calculate_customs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text.strip())
        price = context.user_data['price']
        engine_size = context.user_data['engine_size']

        import_duty = price * 0.10
        base_rate = 50 if engine_size <= 3000 else 100
        age_coeff = min(age, 15) if age > 0 else 1
        excise_tax = base_rate * (engine_size / 1000) * age_coeff
        vat = (price + import_duty + excise_tax) * 0.20
        total_payment = import_duty + excise_tax + vat

        result_text = (
            f"Результати розрахунку\n"
            f"Загальна сума митних платежів: {total_payment:,.2f} €\n"
            f"Загальна вартість авто з розмитненням: {price + total_payment:,.2f} €"
        )
        await update.message.reply_text(result_text)

    except (ValueError, KeyError):
        await update.message.reply_text("Сталася помилка. Будь ласка, введіть коректні дані.")

    context.user_data.clear()
    return await start(update, context)