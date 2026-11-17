import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, service_selected, email_received, add_admin, remove_admin, list_admins
from database import init_db

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
)
logger = logging.getLogger(__name__)

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    owner_id = os.environ["OWNER_TELEGRAM_ID"]
    if not owner_id.isdigit():
        raise RuntimeError("OWNER_TELEGRAM_ID must be your numeric Telegram user ID.")

    init_db()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("admins", list_admins))
    app.add_handler(CallbackQueryHandler(service_selected, pattern=r"^service:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_received))

    logger.info("Service Mail Notifier is starting in polling mode.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
