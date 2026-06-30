import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import TELEGRAM_TOKEN
from bot.handlers import start, reset, handle_message, handle_document

logging.basicConfig(level=logging.INFO)

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN не задан")

app = Flask(__name__)

bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("reset", reset))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, bot_app.bot)
        asyncio.run(bot_app.process_update(update))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run()