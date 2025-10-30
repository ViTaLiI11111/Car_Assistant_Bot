import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from services.vision_analyzer import analyze_car_damage
from services import database
from .common import start

logger = logging.getLogger(__name__)
REPAIR_PHOTO = 1

async def repair_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Будь ласка, надішліть фото вашого авто для попередньої оцінки вартості ремонту."
    )
    return REPAIR_PHOTO

async def repair_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Аналізую фото, зачекайте... Це може зайняти до хвилини.")
    user_id = update.message.from_user.id

    try:
        photo_file_id = update.message.photo[-1].file_id
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        analysis_result = analyze_car_damage(image_bytes=bytes(photo_bytes))

        if not analysis_result or "error" in analysis_result:
            error_message = analysis_result.get("error", "Не вдалося обробити зображення.") if analysis_result else "Не вдалося обробити зображення."
            await update.message.reply_text(f"Виникла помилка: {error_message}")
        else:
            min_cost = analysis_result.get('estimated_cost_min', 0)
            max_cost = analysis_result.get('estimated_cost_max', 0)
            description = analysis_result.get('damage_description', 'Опис відсутній.')
            brand = analysis_result.get('car_brand', 'Марка не визначена.')
            currency = analysis_result.get('currency', 'UAH')
            model_name = analysis_result.get('model_used', 'невідома')

            case_data_to_save = {
                'user_id': user_id,
                'telegram_photo_id': photo_file_id,
                'car_brand': brand,
                'damage_description': description,
                'estimated_cost_min': min_cost,
                'estimated_cost_max': max_cost
            }
            database.add_user_case(case_data_to_save)
            logger.info(f"Збережено новий кейс для користувача {user_id}")

            response_text = (
                f"**Результати попередньої оцінки:**\n\n"
                f"**Модель та марка:**\n{brand}\n"
                f"🔍 **Виявлені пошкодження:**\n_{description}_\n\n"
                f"💰 **Орієнтовна вартість ремонту:**\n"
                f"Від **{min_cost:,}** до **{max_cost:,} {currency}**.\n\n"
                f"_Цей аналіз збережено у вашу персональну історію._\n\n"
                f"Назва асистента: {model_name}."
            )
            await update.message.reply_text(response_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Критична помилка в обробнику фото: {e}")
        await update.message.reply_text("Сталася непередбачувана помилка. Спробуйте пізніше.")

    return await start(update, context)