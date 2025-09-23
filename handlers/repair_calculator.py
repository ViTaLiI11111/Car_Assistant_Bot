from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import logging

import services.vision_analyzer
from services.vision_analyzer import analyze_car_damage
from .common import start

logger = logging.getLogger(__name__)

REPAIR_PHOTO = 1

async def repair_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запускає процес розрахунку вартості ремонту."""
    await update.message.reply_text(
        "Будь ласка, надішліть фото вашого авто для попередньої оцінки вартості ремонту.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return REPAIR_PHOTO

async def repair_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Аналізую фото, зачекайте... Це може зайняти до хвилини.")

    try:
        photo_file = await update.message.photo[-1].get_file()

        # Завантажуємо фото в пам'ять у вигляді байтів
        photo_bytes = await photo_file.download_as_bytearray()

        analysis_result = analyze_car_damage(image_bytes=bytes(photo_bytes))

        if not analysis_result or "error" in analysis_result:
            error_message = analysis_result.get("error", "Не вдалося обробити зображення.") if analysis_result else "Не вдалося обробити зображення."
            await update.message.reply_text(f"Виникла помилка: {error_message}")
        else:
            min_cost = analysis_result.get('estimated_cost_min', 0)
            max_cost = analysis_result.get('estimated_cost_max', 0)
            description = analysis_result.get('damage_description', 'Опис відсутній.')
            brand = analysis_result.get('car_brand', 'Опис відсутній.')
            currency = analysis_result.get('currency', 'UAH')
            model_name = analysis_result.get('model_used', 'Опис відсутній.')

            response_text = (
                f"**Результати попередньої оцінки:**\n\n"
                f"**Модель та марка:**\n{brand}\n"
                f"🔍 **Виявлені пошкодження:**\n_{description}_\n\n"
                f"💰 **Орієнтовна вартість ремонту:**\n"
                f"Від **{min_cost:,}** до **{max_cost:,} {currency}**.\n\n"
                f"_Зверніть увагу, це автоматична оцінка. Для точного розрахунку зверніться до менеджера._\n\n\n\n"
                f"Назва асистента, який надав вам послугу аналізу:\n{model_name}.\n\n**"
            )
            await update.message.reply_text(response_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Критична помилка в обробнику фото: {e}")
        await update.message.reply_text("Сталася непередбачувана помилка. Спробуйте пізніше.")

    return await start(update, context)