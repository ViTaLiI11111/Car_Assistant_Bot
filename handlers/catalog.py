import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from services import database

logger = logging.getLogger(__name__)


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['history_page'] = 1
    await display_history_card(update, context)


async def display_history_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    current_page = context.user_data.get('history_page', 1)

    case, total_cases = database.get_user_case_by_page(user_id=user_id, page=current_page)

    if not case:
        message_text = "Ваша історія аналізів порожня. Надішліть фото для оцінки, щоб почати."
        if query:
            await query.answer()
            await query.edit_message_text(message_text)
        else:
            await update.message.reply_text(message_text)
        return

    caption_text = (
        f"🚗 **Марка:** {case['car_brand']}\n\n"
        f"🔍 **Опис пошкоджень:**\n_{case['damage_description']}_\n\n"
        f"💰 **Оцінка ремонту:**\n"
        f"Від {case['estimated_cost_min']:,} до {case['estimated_cost_max']:,} UAH\n\n"
        f"🗓️ **Дата аналізу:** {case['created_at'].strftime('%Y-%m-%d %H:%M')}"
    )

    keyboard = []
    row = []
    if current_page > 1:
        row.append(InlineKeyboardButton("⬅️ Попередній", callback_data="history_prev"))

    row.append(InlineKeyboardButton(f"📄 {current_page} / {total_cases}", callback_data="history_nop"))

    if current_page < total_cases:
        row.append(InlineKeyboardButton("Наступний ➡️", callback_data="history_next"))

    keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)

    media = InputMediaPhoto(media=case['telegram_photo_id'], caption=caption_text, parse_mode='Markdown')

    if query:
        await query.answer()
        try:
            await query.edit_message_media(media=media, reply_markup=reply_markup)
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Помилка оновлення історії: {e}")
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=case['telegram_photo_id'],
            caption=caption_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


async def history_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    action = query.data
    current_page = context.user_data.get('history_page', 1)

    if action == 'history_next':
        current_page += 1
    elif action == 'history_prev':
        current_page -= 1
    else:
        await query.answer("Це номер поточної сторінки");
        return

    context.user_data['history_page'] = current_page
    await display_history_card(update, context)