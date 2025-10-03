import logging
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN

from handlers.common import start, cancel, CHOOSING, handle_unsupported_messages
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

    unsupported_filter = filters.VOICE | filters.VIDEO_NOTE

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Розрахунок вартості ремонту$"), repair_start),
                MessageHandler(filters.Regex("^Калькулятор розмитнення$"), customs_start),
                MessageHandler(unsupported_filter, handle_unsupported_messages),
            ],
            REPAIR_PHOTO: [
                MessageHandler(filters.PHOTO, repair_photo_received),
                MessageHandler(unsupported_filter, handle_unsupported_messages),
            ],
            ASK_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_price),
                MessageHandler(unsupported_filter, handle_unsupported_messages),
            ],
            ASK_ENGINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_engine),
                MessageHandler(unsupported_filter, handle_unsupported_messages),
            ],
            ASK_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_customs),
                MessageHandler(unsupported_filter, handle_unsupported_messages),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()