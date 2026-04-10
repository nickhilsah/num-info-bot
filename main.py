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
def home(): return "BOT READY ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- UNIFIED FORMATTER ---
def format_unified_response(data_list, search_num):
    if not data_list:
        return "<b>❌ NO RECORD FOUND</b>"

    # Data Containers (Sets use kar rahe hain duplicates hatane ke liye)
    all_numbers = set()
    names = set()
    fathers = set()
    addresses = set()
    aadhaars = set()
    networks = set()
    
    # Search kiya gaya number hamesha list mein rahega
    all_numbers.add(search_num)

    for info in data_list:
        def clean(key):
            val = str(info.get(key, "")).strip()
            return val if val.lower() not in ["n/a", "null", "undefined", "none", ""] else None

        # Info extraction
        n = clean('name')
        if n: names.add(n.upper())
        
        f = clean('fatherName')
        if f: fathers.add(f.upper())

        a = clean('address')
        if a: addresses.add(a.upper())

        aadhaar = clean('aadhaarNumber')
        if aadhaar: aadhaars.add(aadhaar)

        circle = clean('circle')
        if circle: networks.add(circle.upper())

        # Saare mobile aur alternate numbers ko ek hi set mein daalna
        for key in ['mobile', 'alternateNumber']:
            raw_val = clean(key)
            if raw_val:
                # Comma ya space se numbers ko alag karke saaf karna
                for part in raw_val.replace(",", " ").split():
                    digit_only = "".join(filter(str.isdigit, part))
                    if len(digit_only) >= 10:
                        all_numbers.add(digit_only)

    # Response Messaging
    lines = []
    lines.append("<b>💎 MASTER DATA RECORD</b>")
    lines.append(f"<b>🎯 TARGET:</b> <code>{search_num}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    
    if names:
        lines.append(f"👤 <b>NAME:</b> <code>{', '.join(names)}</code>")
    
    if fathers:
        lines.append(f"👨‍👦 <b>FATHER:</b> <code>{', '.join(fathers)}</code>")

    if aadhaars:
        lines.append(f"🆔 <b>AADHAAR:</b> <code>{', '.join(aadhaars)}</code>")

    if networks:
        lines.append(f"🌍 <b>CIRCLE:</b> <code>{', '.join(networks)}</code>")

    if addresses:
        lines.append(f"🏠 <b>ADDRESS:</b>\n┗━━» <i>{', '.join(addresses)}</i>")

    # Yahan saare numbers ek saath aayenge
    lines.append("\n📱 <b>ALL NUMBERS (Tap to Copy):</b>")
    for num in sorted(all_numbers):
        # <code> tag se Telegram click-to-copy enable kar deta hai
        lines.append(f"┗━━» <code>{num}</code>")
    
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\nNumber bhejein, saare linked numbers aur Aadhaar details ek saath milenge.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ Kripya valid number bhejien.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Fetching All Linked Data...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=20) as response:
                if response.status == 200:
                    json_res = await response.json()
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No Record Found.</b>")
                        return

                    final_output = format_unified_response(records, number)
                    await wait.edit_text(final_output, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> {response.status}")
    except Exception:
        await wait.edit_text("<b>❌ Error:</b> Connection fail ho gaya.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
    
