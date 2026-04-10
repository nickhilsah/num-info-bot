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
    return "SYSTEM ONLINE ✅"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
# IMPORTANT: Reset your token via @BotFather for security!
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE ALL-IN-ONE PREMIUM FORMATTER ---
def format_premium_response(data, number):
    # API Response check
    if isinstance(data, list) and len(data) > 0:
        info = data[0]
    elif isinstance(data, dict):
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            info = data['data'][0]
        else:
            info = data
    else:
        return "<b>❌ KOI RECORD NAHI MILA</b>"

    # ALL POSSIBLE MAPPING KEYS
    mapping = {
        'name': '👤 <b>FULL NAME</b>',
        'fatherName': '👨‍👦 <b>FATHER NAME</b>',
        'dob': '📅 <b>DATE OF BIRTH</b>',
        'gender': '🚻 <b>GENDER</b>',
        'address': '🏠 <b>ADDRESS</b>',
        'city': '🏙️ <b>CITY/TOWN</b>',
        'pincode': '📍 <b>PINCODE</b>',
        'state': '🗺️ <b>STATE</b>',
        'aadhaarNumber': '🆔 <b>AADHAAR NUMBER</b>',
        'voterId': '🗳️ <b>VOTER ID</b>',
        'alternativeNumber': '📞 <b>ALTERNATIVE NO.</b>',
        'operator': '📡 <b>NETWORK OPERATOR</b>',
        'circle': '🌍 <b>NETWORK CIRCLE</b>',
        'activationDate': '⏳ <b>ACTIVATION DATE</b>',
        'imsi': '🔢 <b>IMSI NUMBER</b>',
        'status': '🟢 <b>STATUS</b>'
    }

    lines = []
    lines.append("<b>💎 ——— PREMIUM DETAILS ——— 💎</b>\n")
    lines.append(f"<b>📱 TARGET :</b> <code>{number}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
    
    found = False
    for key, label in mapping.items():
        value = info.get(key)
        
        # Filtering values: Jo data API mein hoga wahi dikhega
        if value and str(value).strip() and str(value).lower() not in ["n/a", "none", "null", "undefined", "false"]:
            val_str = str(value).upper()
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
        "<b>👋 Swagat Hai!</b>\n\n"
        "10-digit mobile number bhejein, main saari available details nikaal dunga."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Number cleanup
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ INVALID:</b> Sahi 10-digit number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Fetching All Records...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=15) as response:
                if response.status == 200:
                    json_res = await response.json()
                    final_msg = format_premium_response(json_res, number)
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> Server Code {response.status}")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await wait.edit_text("<b>❌ ERROR:</b> API connect nahi ho rahi.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is LIVE with Full Mapping!")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
