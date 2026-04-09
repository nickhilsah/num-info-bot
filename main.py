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
def home(): return "SYSTEM ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DALO"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE ULTIMATE FORMATTER ---
def format_ultra_clean(data, number):
    if not data or not isinstance(data, dict):
        return f"<b>📝 RESULT FOR:</b> <code>{number}</code>\n\n{data}"

    # Sirf kaam ki jaankari dikhayenge
    lines = []
    lines.append("<b>╔══════════════════╗</b>")
    lines.append("<b>       NUM INFO LOOKUP     </b>")
    lines.append("<b>╚══════════════════╝</b>")
    lines.append(f"<b>📍 TARGET :</b> <code>{number}</code>\n")
    
    # Mapping keys to better names
    mapping = {
        'name': '👤 NAME',
        'operator': '📶 OPERATOR',
        'circle': '🌍 CIRCLE',
        'state': '📍 STATE',
        'type': 'ℹ️ TYPE',
        'carrier': '🏢 CARRIER',
        'last_seen': '🕒 LAST SEEN'
    }

    found = False
    for key, value in data.items():
        # Check if we have a pretty name or use the raw key
        label = mapping.get(key.lower(), f"🔹 {key.upper()}")
        
        # JUNK filter
        if key.lower() not in ['status', 'success', 'v', 'api'] and value:
            lines.append(f"<b>{label} :</b> <code>{value}</code>")
            found = True
            
    if not found:
        return "<b>❌ NO RECORD FOUND IN DATABASE</b>"

    lines.append("\n<b>⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯</b>")
    lines.append("<b>✅ DATA FETCHED SUCCESSFULLY</b>")
    
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>👋 Number Lookup Bot Me Swagat Hai!</b>\n\n"
        "Sirf 10-digit number bhejiye, details niche milengi."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ INVALID:</b> 10-digit number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=10) as response:
                if response.status == 200:
                    try:
                        json_res = await response.json()
                        final_msg = format_ultra_clean(json_res, number)
                    except:
                        raw = await response.text()
                        final_msg = f"<b>📝 DETAILS:</b>\n<code>{raw}</code>"
                    
                    # HTML parse mode use ho raha hai yahan
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ ERROR:</b> Server Code {response.status}")
    
    except Exception:
        await wait.edit_text("<b>❌ TIMEOUT:</b> API connect nahi ho pa rahi.")

def main():
    keep_alive()
    # Build with HTML support
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
