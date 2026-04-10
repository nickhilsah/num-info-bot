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
def home(): return "UNIFIED BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- UNIFIED MASTER FORMATTER ---
def format_unified_response(data_list, search_num):
    if not data_list:
        return "<b>❌ NO RECORD FOUND</b>"

    # Sets use kar rahe hain taaki duplicate data automatically hat jaye
    all_numbers = {search_num} # Search number pehle se add hai
    names = set()
    fathers = set()
    addresses = set()
    aadhaars = set()
    circles = set()

    # Saare 4-5 jitne bhi records hain, unka loop
    for info in data_list:
        def get_clean(key):
            v = str(info.get(key, "")).strip()
            return v if v.lower() not in ["n/a", "null", "undefined", "none", ""] else None

        # Data collect karna
        if get_clean('name'): names.add(get_clean('name').upper())
        if get_clean('fatherName'): fathers.add(get_clean('fatherName').upper())
        if get_clean('address'): addresses.add(get_clean('address').upper())
        if get_clean('aadhaarNumber'): aadhaars.add(get_clean('aadhaarNumber'))
        if get_clean('circle'): circles.add(get_clean('circle').upper())

        # Alternative aur Mobile numbers ko extract karke ek saath lana
        for key in ['mobile', 'alternateNumber']:
            val = get_clean(key)
            if val:
                # Agar ek hi line mein multiple numbers hon comma/space ke saath
                for part in val.replace(",", " ").split():
                    num = "".join(filter(str.isdigit, part))
                    if len(num) >= 10:
                        all_numbers.add(num)

    # Final Output taiyar karna
    lines = []
    lines.append("<b>💎 UNIFIED MASTER RECORD</b>")
    lines.append(f"<b>🎯 TARGET:</b> <code>{search_num}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    
    if names:
        lines.append(f"👤 <b>NAME:</b> <code>{', '.join(names)}</code>")
    
    if fathers:
        lines.append(f"👨‍👦 <b>FATHER:</b> <code>{', '.join(fathers)}</code>")

    if aadhaars:
        lines.append(f"🆔 <b>AADHAAR:</b> <code>{', '.join(aadhaars)}</code>")

    if circles:
        lines.append(f"🌍 <b>CIRCLE:</b> <code>{', '.join(circles)}</code>")

    if addresses:
        # Address ko list format mein dikhana kyunki ye bade hote hain
        lines.append("\n🏠 <b>ADDRESS(ES):</b>")
        for addr in addresses:
            lines.append(f"┗» <i>{addr}</i>")

    # Saare numbers ek hi header ke niche "Tap to Copy" mode mein
    lines.append("\n📱 <b>ALL LINKED NUMBERS (Tap to Copy):</b>")
    # Search number ko chhod kar baki numbers ko sort karke dikhana
    sorted_numbers = sorted(list(all_numbers))
    for num in sorted_numbers:
        lines.append(f"┗━━» <code>{num}</code>")
    
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>👋 Swagat Hai!</b>\n\nNumber bhejein, main saare records merge karke ek hi list bana dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not number.isdigit() or len(number) < 10:
        await update.message.reply_html("<b>⚠️ Kripya 10-digit number bhejien.</b>")
        return

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
