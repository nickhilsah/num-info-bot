import os
import requests
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask server Render ko zinda rakhne ke liye
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- BOT CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

async def start(update, context):
    await update.message.reply_text("Render Bot Active! Number bhejein.")

async def handle_message(update, context):
    num = update.message.text.strip()
    if num.isdigit():
        res = requests.get(f"{API_URL}{num}").text
        await update.message.reply_text(f"Result:\n{res}")

def main():
    Thread(target=run).start()
    bot = Application.builder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.run_polling()

if __name__ == '__main__':
    main()
