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

# --- THE ULTIMATE EMOJI FORMATTER ---
def format_with_emojis(data, number):
    if not data or not isinstance(data, dict):
        return f"<b>🔎 RESULT FOR:</b> <code>{number}</code>\n\n{data}"

    # Mapping keys to beautiful emojis and labels
    mapping = {
        'name': '👤 <b>NAME</b>',
        'operator': '📶 <b>OPERATOR</b>',
        'circle': '🌍 <b>CIRCLE</b>',
        'state': '📍 <b>STATE</b>',
        'type': 'ℹ️ <b>SIM TYPE</b>',
        'carrier': '🏢 <b>CARRIER</b>',
        'last_seen': '🕒 <b>LAST SEEN</b>',
        'location': '🗺 <b>LOCATION</b>'
    }

    lines = []
    lines.append("<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n")
    lines.append(f"<b>📱 TARGET :</b> <code>{number}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n")
    
    found = False
    for key, value in data.items():
        k_lower = key.lower()
        if k_lower in mapping and value:
            label = mapping[k_lower]
            lines.append(f"{label}\n┗━━» <code>{value}</code>\n")
            found = True
            
    # Agar kuch naya data aaye jo mapping mein nahi hai
    if not found:
        for key, value in data.items():
            if key.lower() not in ['status', 'success', 'v', 'api'] and value:
                lines.append(f"<b>🔹 {key.upper()}</b>\n┗━━» <code>{value}</code>\n")
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
        "Sirf mobile number bhejein aur details <b>Emojis</b> ke saath paayein."
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
                        json_res = await response.json()
                        final_msg = format_with_emojis(json_res, number)
                    except:
                        raw = await response.text()
                        final_msg = f"<b>📝 DETAILS:</b>\n<code>{raw}</code>"
                    
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ ERROR:</b> API Offline ({response.status})")
    
    except Exception:
        await wait.edit_text("<b>❌ TIMEOUT:</b> API connect nahi hui.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
