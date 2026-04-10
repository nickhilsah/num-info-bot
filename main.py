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
# @BotFather se naya token lekar yahan dalein
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- THE UNIVERSAL PREMIUM FORMATTER ---
def format_premium_response(data, number):
    if isinstance(data, list) and len(data) > 0:
        info = data[0]
    elif isinstance(data, dict):
        info = data.get('data', [data])[0] if isinstance(data.get('data'), list) else data
    else:
        return "<b>❌ KOI RECORD NAHI MILA</b>"

    # Universal Mapping: Har possible key jo ek API bhej sakti hai
    mapping = {
        # Identity
        'name': '👤 <b>FULL NAME</b>',
        'full_name': '👤 <b>FULL NAME</b>',
        'customer_name': '👤 <b>FULL NAME</b>',
        'fatherName': '👨‍👦 <b>FATHER NAME</b>',
        'father_name': '👨‍👦 <b>FATHER NAME</b>',
        'dob': '📅 <b>DATE OF BIRTH</b>',
        'date_of_birth': '📅 <b>DATE OF BIRTH</b>',
        'gender': '🚻 <b>GENDER</b>',
        
        # Identity Numbers
        'aadhaarNumber': '🆔 <b>AADHAAR NUMBER</b>',
        'aadhaar_no': '🆔 <b>AADHAAR NUMBER</b>',
        'uid': '🆔 <b>AADHAAR NUMBER</b>',
        'voterId': '🗳️ <b>VOTER ID</b>',
        'voter_no': '🗳️ <b>VOTER ID</b>',
        'epic_no': '🗳️ <b>VOTER ID</b>',
        
        # Contact & Alt Numbers
        'alternativeNumber': '📞 <b>ALT NUMBER</b>',
        'altNumber': '📞 <b>ALT NUMBER</b>',
        'alt_number': '📞 <b>ALT NUMBER</b>',
        'alternate_no': '📞 <b>ALT NUMBER</b>',
        'mobile2': '📞 <b>ALT NUMBER</b>',
        'contact2': '📞 <b>ALT NUMBER</b>',
        'email': '📧 <b>EMAIL ID</b>',
        
        # Location & Address
        'address': '🏠 <b>ADDRESS</b>',
        'permanent_address': '🏠 <b>ADDRESS</b>',
        'city': '🏙️ <b>CITY</b>',
        'district': '🏙️ <b>DISTRICT</b>',
        'state': '🗺️ <b>STATE</b>',
        'pincode': '📍 <b>PINCODE</b>',
        'zip': '📍 <b>PINCODE</b>',
        
        # Network & SIM Info
        'operator': '📡 <b>NETWORK</b>',
        'carrier': '📡 <b>NETWORK</b>',
        'circle': '🌍 <b>CIRCLE/REGION</b>',
        'activationDate': '⏳ <b>ACTIVATION</b>',
        'status': '🟢 <b>SIM STATUS</b>',
        'imsi': '🔢 <b>IMSI</b>',
        'iccid': '🔢 <b>ICCID/SSN</b>'
    }

    lines = []
    lines.append("<b>💎 ——— PREMIUM DETAILS ——— 💎</b>\n")
    lines.append(f"<b>📱 TARGET :</b> <code>{number}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
    
    found = False
    displayed_labels = set()

    # Smart Filtering Loop
    for key, label in mapping.items():
        value = info.get(key)
        if value and str(value).strip() and str(value).lower() not in ["n/a", "none", "null", "undefined", "false", "0"]:
            if label not in displayed_labels:
                val_str = str(value).upper()
                lines.append(f"{label}\n┗━━» <b>{val_str}</b>\n")
                found = True
                displayed_labels.add(label)
            
    if not found:
        return "<b>❌ NO DATA FOUND IN DATABASE</b>"

    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    lines.append("<b>✅ SUCCESS : DATA FETCHED</b>")
    
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\n10-digit number bhejein.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ 10-digit number bhejein.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Searching All Databases...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=20) as response:
                if response.status == 200:
                    json_res = await response.json()
                    # Console log for you to see hidden keys
                    print(f"Full Data for {number}: {json_res}")
                    
                    final_msg = format_premium_response(json_res, number)
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> {response.status}")
    except Exception as e:
        await wait.edit_text("<b>❌ TIMEOUT:</b> API slow hai.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
