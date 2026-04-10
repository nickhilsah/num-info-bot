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
def home(): return "MASTER BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MASTER UNIFIED FORMATTER ---
def format_single_master_record(data_list, search_num):
    if not data_list:
        return "<b>❌ NO RECORD FOUND</b>"

    # Sab data ek jagah jama karne ke liye sets
    names = set()
    fathers = set()
    addresses = set()
    aadhaars = set()
    circles = set()
    alt_numbers = set()

    # Saare records ko loop karke data nikalna
    for info in data_list:
        def get_v(key):
            val = str(info.get(key, "")).strip()
            return val if val.lower() not in ["n/a", "null", "none", ""] else None

        if get_v('name'): names.add(get_v('name').upper())
        if get_v('fatherName'): fathers.add(get_v('fatherName').upper())
        if get_v('address'): addresses.add(get_v('address').upper())
        if get_v('aadhaarNumber'): aadhaars.add(get_v('aadhaarNumber'))
        if get_v('circle'): circles.add(get_v('circle').upper())

        # Mobile aur Alternate numbers ko ek sath handle karna
        for key in ['mobile', 'alternateNumber']:
            raw_num = get_v(key)
            if raw_num:
                # Comma ya space se numbers alag karna
                for part in raw_num.replace(",", " ").split():
                    clean_num = "".join(filter(str.isdigit, part))
                    # Sirf 10 digit wale aur non-target numbers ko alt mein daalna
                    if len(clean_num) >= 10 and clean_num != search_num:
                        alt_numbers.add(clean_num)

    # Response Messaging (Ek hi message banane ka logic)
    lines = []
    lines.append("<b>💎 UNIFIED MASTER RECORD</b>")
    lines.append(f"<b>🎯 TARGET:</b> <code>{search_num}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    
    if names: lines.append(f"👤 <b>NAME:</b> <code>{', '.join(names)}</code>")
    if fathers: lines.append(f"👨‍👦 <b>FATHER:</b> <code>{', '.join(fathers)}</code>")
    if aadhaars: lines.append(f"🆔 <b>AADHAAR:</b> <code>{', '.join(aadhaars)}</code>")
    if circles: lines.append(f"🌍 <b>CIRCLE:</b> <code>{', '.join(circles)}</code>")
    
    # Address agar multiple hain toh clean dikhana
    if addresses:
        lines.append("\n🏠 <b>ADDRESS:</b>")
        for addr in addresses:
            lines.append(f"┗» <i>{addr}</i>")

    # SABSE ZAROORI: Saare Alt numbers ek sath
    lines.append("\n📞 <b>ALT NUMBERS (Tap to Copy):</b>")
    if alt_numbers:
        # Har number ko <code> tag mein daalna takay har ek par click karke copy ho sake
        copy_list = [f"<code>{n}</code>" for n in sorted(alt_numbers)]
        lines.append(f"┗━━» {', '.join(copy_list)}")
    else:
        lines.append("┗━━» <i>No extra numbers found.</i>")
    
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>Bhejiye Number!</b>\nSaare records merge karke ek hi message mein dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ 10-digit number bhejien.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Merging all records...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=15) as response:
                if response.status == 200:
                    json_res = await response.json()
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No Record Found.</b>")
                        return

                    # Saare data ko ek hi function mein merge kar diya
                    final_msg = format_single_master_record(records, number)
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API Error:</b> {response.status}")
    except Exception:
        await wait.edit_text("<b>❌ Error:</b> Connection failed.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    wait = await update.message.reply_html("<b>⚡ Fetching & Merging Records...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{number}", timeout=15) as response:
                if response.status == 200:
                    json_res = await response.json()
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No Record Found.</b>")
                        return

                    # Yahan hum saare 4 records ko format_unified_response mein bhej rahe hain
                    final_msg = format_unified_response(records, number)
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API Server Error:</b> {response.status}")
    except Exception:
        await wait.edit_text("<b>❌ ERROR:</b> Data merge nahi ho pa raha.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
