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
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE NEXT-LINE FORMATTER ---
def format_ultra_clean(data, number):
    # API agar list bhej rahi hai toh pehla item nikalein
    if isinstance(data, list) and len(data) > 0:
        info = data[0]
    elif isinstance(data, dict):
        info = data
    else:
        return None

    if not info: return None

    # Mapping keys to labels (Aapki API ke hisab se)
    mapping = {
        'name': '👤 <b>FULL NAME</b>',
        'fatherName': '👨‍👦 <b>FATHER NAME</b>',
        'circle': '🌍 <b>NETWORK CIRCLE</b>',
        'address': '🏠 <b>ADDRESS</b>',
        'aadhaarNumber': '🆔 <b>AADHAAR NUMBER</b>'
    }

    lines = []
    lines.append("<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n")
    lines.append(f"<b>📱 TARGET :</b> <code>{number}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
    
    found = False
    for key, label in mapping.items():
        value = info.get(key)
        if value and str(value).strip() and str(value).lower() != "n/a":
            # Value ko uppercase karna
            val_str = str(value).upper()
            # YAHAN CHANGE KIYA HAI: Label ke baad \n (Next Line) dala hai
            lines.append(f"{label}\n┗━━» <b>{val_str}</b>\n")
            found = True
            
    if not found:
        return "<b>❌ NO RECORD FOUND IN DATABASE</b>"

    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    lines.append("<b>✅ SUCCESS : DATA FETCHED</b>")
    
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>👋 Number Lookup Bot Me Swagat Hai!</b>\n\n"
        "Sirf 10-digit number bhejiye, details niche milengi."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Number cleaning (+91 ya spaces hatane ke liye)
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ INVALID:</b> 10-digit number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=15) as response:
                if response.status == 200:
                    json_res = await response.json()
                    # Formatting call
                    final_msg = format_ultra_clean(json_res, number)
                    
                    if final_msg:
                        await wait.edit_text(final_msg, parse_mode='HTML')
                    else:
                        await wait.edit_text("<b>❌ NO RECORD FOUND</b>")
                else:
                    await wait.edit_text(f"<b>❌ ERROR:</b> Server Code {response.status}")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await wait.edit_text("<b>❌ TIMEOUT:</b> API connect nahi ho pa rahi.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is LIVE with Next-Line Layout!")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
