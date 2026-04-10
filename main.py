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
def home(): return "BOT STATUS: ONLINE 🚀"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DALO"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE FIX: DATA PARSER ---
def format_with_emojis(data, number):
    # Agar data list hai (jaise aapka hai), toh pehla element nikal lo
    if isinstance(data, list) and len(data) > 0:
        info = data[0]
    elif isinstance(data, dict):
        info = data
    else:
        return f"<b>🔎 RESULT FOR:</b> <code>{number}</code>\n\n{data}"

    # Mapping keys to beautiful emojis and labels
    mapping = {
        "<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n\n"
                f"<b>📱 TARGET :</b> <code>{num}</code>\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
                f"👤 <b>NAME</b>\n┗━━» <code>{name}</code>\n\n"
                f"👨‍👦 <b>FATHER NAME</b>\n┗━━» <code>{f_name}</code>\n\n"
                f"🌍 <b>CIRCLE</b>\n┗━━» <code>{circle}</code>\n\n"
                f"🏠 <b>ADDRESS</b>\n┗━━» <code>{addr}</code>\n\n"
                f"🆔 <b>AADHAAR NO</b>\n┗━━» <code>{adhar}</code>\n\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                "<b>✅ DATA FETCHED</b>"'
    }

    lines = []
    lines.append("<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n")
    lines.append(f"<b>📱 TARGET :</b> <code>{number}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
    
    found = False
    for key, label in mapping.items():
        # Dictionary mein check karo agar key maujood hai aur value khali nahi hai
        value = info.get(key)
        if value and str(value).strip():
            lines.append(f"{label}\n┗━━» <code>{value}</code>\n")
            found = True
            
    if not found:
        return "<b>❌ DATA NOT FOUND IN DATABASE</b>"

    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    lines.append("<b>✅ SUCCESS : DATA FETCHED</b>")
    
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>👋 Swagat Hai!</b>\n\n"
        "Sirf mobile number bhejein aur details <b>Premium Design</b> mein paayein."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ ERROR:</b> Valid number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=10) as response:
                if response.status == 200:
                    try:
                        # API se JSON data le rahe hain
                        json_res = await response.json()
                        final_msg = format_with_emojis(json_res, number)
                    except Exception as e:
                        # Agar JSON fail ho jaye
                        raw = await response.text()
                        final_msg = f"<b>📝 DETAILS:</b>\n<code>{raw}</code>"
                    
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ ERROR:</b> API Offline ({response.status})")
    
    except Exception as e:
        await wait.edit_text(f"<b>❌ TIMEOUT:</b> API connect nahi hui.\n{str(e)}")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
