import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import TELEGRAM_TOKEN

from bot.handlers import start, reset, handle_message, handle_document

logging.basicConfig(level=logging.INFO)

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN не задан в .env файле")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("Бот запущен и готов принимать файлы договоров (PDF/DOCX)...")
    app.run_polling()


if __name__ == "__main__":
    main()
