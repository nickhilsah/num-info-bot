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
def home(): return "PREMIUM MULTI-BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
# @BotFather se naya token lekar yahan replace karein
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv6.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- PREMIUM FORMATTER WITH TAP-TO-COPY ---
def format_premium_response(data_list, search_num):
    if not data_list or not isinstance(data_list, list):
        return ["<b>❌ NO RECORD FOUND</b>"]

    # Mapping based on your API JSON structure
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
    
    # Process up to 5 records to keep it clean and avoid spam
    for i, info in enumerate(data_list[:5], 1):
        lines = []
        lines.append(f"<b>💎 RECORD #{i}</b>")
        lines.append(f"<b>🎯 TARGET :</b> <code>{search_num}</code>")
        lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
        
        found_data = False
        for key, label in mapping.items():
            value = info.get(key)
            # Skip empty or useless data
            if value and str(value).strip() and str(value).lower() not in ["n/a", "null", "undefined", ""]:
                val_str = str(value).upper()
                # <code> tag enables Tap-to-Copy
                lines.append(f"{label}\n┗━━» <code>{val_str}</code>\n")
                found_data = True
        
        if found_data:
            lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
            lines.append("<b>✅ SUCCESS : DATA FETCHED</b>")
            formatted_messages.append("\n".join(lines))

    return formatted_messages

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        "<b>👋 Swagat Hai!</b>\n\n"
        "10-digit number bhejein, saare records (Tap-to-Copy) ke saath milenge."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cleaning the input number
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ INVALID:</b> Sahi 10-digit number bhejein.")
        return

    wait = await update.message.reply_html("<b>⚡ Searching Premium Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=25) as response:
                if response.status == 200:
                    json_res = await response.json()
                    # Extracting the list from "data" key
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No records found in database.</b>")
                        return

                    results = format_premium_response(records, number)
                    
                    # Edit the first 'searching' message with the first result
                    await wait.edit_text(results[0], parse_mode='HTML')
                    
                    # Send additional records as new messages
                    for extra_msg in results[1:]:
                        await update.message.reply_html(extra_msg)
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> Status Code {response.status}")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await wait.edit_text("<b>❌ ERROR:</b> API response nahi de rahi ya slow hai.")

def main():
    # Keep the web server alive for Replit/UptimeRobot
    keep_alive()
    
    # Initialize the Bot
    app_bot = Application.builder().token(BOT_TOKEN).build()
    
    # Add Handlers
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is LIVE! Multi-result and Tap-to-copy enabled.")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
