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
def home(): return "BOT STATUS: ACTIVE 🚀"

def run_flask(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DALO"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE FORMATTER (As per your request) ---
def format_premium_output(data, num):
    # API agar list bhej rahi hai toh pehla item nikalein
    if isinstance(data, list) and len(data) > 0:
        info = data[0]
    elif isinstance(data, dict):
        info = data
    else:
        return None

    if not info: return None

    # Values extract karna
    name = str(info.get("name", "N/A")).upper()
    f_name = str(info.get("fatherName", "N/A")).upper()
    circle = str(info.get("circle", "N/A")).upper()
    addr = str(info.get("address", "N/A")).upper()
    adhar = str(info.get("aadhaarNumber", "N/A"))

    # Aapka bataya hua format
    lines = [
        "<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n",
        f"<b>📱 TARGET :</b> <code>{num}</code>",
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n",
        f"👤 <b>NAME</b>\n┗━━» <b>{name}</b>\n",
        f"👨‍👦 <b>FATHER NAME</b>\n┗━━» <b>{f_name}</b>\n",
        f"🌍 <b>CIRCLE</b>\n┗━━» <b>{circle}</b>\n",
        f"🏠 <b>ADDRESS</b>\n┗━━» <b>{addr}</b>\n",
        f"🆔 <b>AADHAAR NO</b>\n┗━━» <code>{adhar}</code>\n",
        "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯",
        "<b>✅ SUCCESS : DATA FETCHED</b>"
    ]
    
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\nNumber bhejiye, details naye format mein milengi.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Number cleaning
    num = update.message.text.strip().replace(" ", "").replace("+91", "")
    
    if not num.isdigit() or len(num) < 10:
        await update.message.reply_html("<b>⚠️ ERROR:</b> Sahi number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{num}", timeout=15) as response:
                if response.status == 200:
                    json_res = await response.json()
                    final_msg = format_premium_output(json_res, num)
                    
                    if final_msg:
                        await wait.edit_text(final_msg, parse_mode='HTML')
                    else:
                        await wait.edit_text("<b>❌ NO RECORD FOUND</b>")
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> Code {response.status}")
    
    except Exception as e:
        await wait.edit_text("<b>❌ ERROR:</b> API connect nahi hui.")

def main():
    keep_alive()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
