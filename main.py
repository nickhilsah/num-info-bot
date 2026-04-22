import os
import logging
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- WEB SERVER (Hosting) ---
app = Flask('')
@app.route('/')
def home(): return "FINAL BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "http://nv6.ek4nsh.in/api/proxy?num="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- FORMATTER (Exact Match for your JSON) ---
def format_premium_response(data_list, search_num):
    if not data_list:
        return ["<b>❌ NO RECORD FOUND</b>"]

    # Nayi API ke hisaab se mapping (CAPITAL aur small keys ka dhyan rakha hai)
    mapping = {
        'NAME': '👤 <b>NAME</b>',
        'fname': '👨‍👦 <b>FATHER</b>',
        'MOBILE': '📱 <b>MOBILE</b>',
        'ADDRESS': '🏠 <b>ADDRESS</b>',
        'circle': '🌍 <b>CIRCLE</b>',
        'alt': '📞 <b>ALT NO</b>',
        'id': '🆔 <b>AADHAAR/ID</b>',
        'email': '📧 <b>EMAIL</b>'
    }

    formatted_messages = []
    
    for i, info in enumerate(data_list[:5], 1): # Top 5 results
        lines = []
        lines.append(f"<b>💎 RECORD #{i}</b>")
        lines.append(f"<b>🎯 TARGET :</b> <code>{search_num}</code>")
        lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
        
        found_any = False
        for key, label in mapping.items():
            value = info.get(key)
            
            # Cleaning and Formatting
            if value and str(value).strip() and str(value).lower() not in ["null", "none", "n/a", ""]:
                # Address se "!" hata kar space lagane ke liye
                val_str = str(value).replace("!", " ").strip().upper()
                lines.append(f"{label}\n┗━━» <code>{val_str}</code>\n")
                found_any = True
        
        if found_any:
            lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
            formatted_messages.append("\n".join(lines))

    return formatted_messages

# --- BOT HANDLERS ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ 10-digit number bhejein.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Searching New Database...</b>")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=25) as response:
                if response.status == 200:
                    json_res = await response.json()
                    
                    # Yahan Galti thi: Nayi API 'results' key use karti hai
                    records = json_res.get("results", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No records found.</b>")
                        return

                    results = format_premium_response(records, number)
                    await wait.edit_text(results[0], parse_mode='HTML')
                    
                    for extra_msg in results[1:]:
                        await update.message.reply_html(extra_msg)
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> Status {response.status}")
    except Exception as e:
        await wait.edit_text(f"<b>❌ ERROR:</b> API Offline hai.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\nNumber bhejein (Tap-to-Copy enabled).")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is LIVE with Nv6 API!")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
                
