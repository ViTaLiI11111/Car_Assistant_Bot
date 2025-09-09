import logging
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN

from handlers.common import start, cancel, CHOOSING
from handlers.repair_calculator import repair_start, repair_photo_received, REPAIR_PHOTO
from handlers.customs_calculator import (
    customs_start,
    ask_price,
    ask_engine,
    calculate_customs,
    ASK_PRICE,
    ASK_ENGINE,
    ASK_AGE,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Розрахунок вартості ремонту$"), repair_start),
                MessageHandler(filters.Regex("^Калькулятор розмитнення$"), customs_start),
            ],
            REPAIR_PHOTO: [MessageHandler(filters.PHOTO, repair_photo_received)],
            ASK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_price)],
            ASK_ENGINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_engine)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_customs)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    logger.info("Бот запускається...")
    application.run_polling()


if __name__ == "__main__":
    main()