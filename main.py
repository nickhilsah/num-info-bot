import os
import logging
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- WEB SERVER (For 24/7 Hosting) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- HELPER FUNCTION (Data Format Karne Ke Liye) ---
def format_response(data):
    """API data ko sundar format mein convert karta hai"""
    if not data:
        return "❌ Koi jaankari nahi mili."
    
    if isinstance(data, dict):
        text = "👤 **User Information**\n"
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        for key, value in data.items():
            # Key ko sundar banane ke liye (e.g. 'full_name' -> 'Full Name')
            clean_key = key.replace('_', ' ').title()
            text += f"🔹 **{clean_key}**: `{value}`\n"
        return text
    
    return f"📝 **Result:**\n`{str(data)}`"

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Number Lookup Bot** mein swagat hai!\n\n"
        "Sirf mobile number bhejiye aur main details nikaal dunga."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_text("⚠️ **Invalid Number!**\nKam se kam 10 digits ka number bhejein.")
        return

    wait_message = await update.message.reply_text("🔍 **Searching...**")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=15) as response:
                if response.status == 200:
                    try:
                        # JSON format check karein
                        json_data = await response.json()
                        final_text = format_response(json_data)
                    except:
                        # Agar JSON nahi hai toh plain text
                        raw_text = await response.text()
                        final_text = f"📝 **Details Found:**\n\n`{raw_text}`"
                    
                    await wait_message.edit_text(final_text, parse_mode='Markdown')
                else:
                    await wait_message.edit_text(f"❌ **Error:** API ne response nahi diya (Status: {response.status})")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await wait_message.edit_text("❌ **Connection Failed!**\nShayad API server offline hai.")

def main():
    keep_alive()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
