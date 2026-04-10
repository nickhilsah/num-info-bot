import os
import logging
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "MULTI-RESULTS BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MULTI-RECORD FORMATTER ---
def format_premium_response(data_list, search_num):
    if not data_list or not isinstance(data_list, list):
        return ["<b>❌ NO RECORD FOUND</b>"]

    mapping = {
        'name': '👤 <b>NAME</b>',
        'fatherName': '👨‍👦 <b>FATHER</b>',
        'mobile': '📱 <b>MOBILE</b>',
        'address': '🏠 <b>ADDRESS</b>',
        'circle': '🌍 <b>CIRCLE</b>',
        'alternateNumber': '📞 <b>ALT NO</b>',
        'aadhaarNumber': '🆔 <b>AADHAAR</b>',
        'email': '📧 <b>EMAIL</b>'
    }

    formatted_messages = []
    
    # Loop through each record found in the API
    for i, info in enumerate(data_list, 1):
        lines = []
        lines.append(f"<b>💎 RECORD #{i}</b>")
        lines.append(f"<b>🎯 TARGET :</b> <code>{search_num}</code>")
        lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
        
        found_data = False
        for key, label in mapping.items():
            value = info.get(key)
            if value and str(value).strip() and str(value).lower() not in ["n/a", "null", "undefined"]:
                lines.append(f"{label}\n┗━━» <b>{str(value).upper()}</b>\n")
                found_data = True
        
        if found_data:
            lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
            formatted_messages.append("\n".join(lines))

    return formatted_messages

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\nNumber bhejein, saare records milenge.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ 10-digit number bhejein.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Multi-Database...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=20) as response:
                if response.status == 200:
                    json_res = await response.json()
                    
                    # API se "data" list nikalna
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No records found.</b>")
                        return

                    results = format_premium_response(records, number)
                    
                    # Pehla result edit karein, baki naye message mein bhejein
                    await wait.edit_text(results[0], parse_mode='HTML')
                    
                    for extra_msg in results[1:5]: # Limit to 5 records to avoid spam
                        await update.message.reply_html(extra_msg)
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> {response.status}")
    except Exception as e:
        await wait.edit_text("<b>❌ ERROR:</b> API connect nahi ho rahi.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
