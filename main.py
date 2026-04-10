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
def home(): return "MASTER UNIFIED BOT ONLINE ✅"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIG ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- MASTER FORMATTER ---
def format_single_master_record(data_list, search_num):
    if not data_list:
        return "<b>❌ NO RECORD FOUND</b>"

    # Data jama karne ke liye sets (Duplicates hatane ke liye)
    names = set()
    fathers = set()
    addresses = set()
    aadhaars = set()
    circles = set()
    linked_numbers = set()

    # Saare 14-15 records ko scan karna
    for info in data_list:
        def get_v(key):
            val = str(info.get(key, "")).strip()
            return val if val.lower() not in ["n/a", "null", "none", ""] else None

        if get_v('name'): names.add(get_v('name').upper())
        if get_v('fatherName'): fathers.add(get_v('fatherName').upper())
        if get_v('address'): addresses.add(get_v('address').upper())
        if get_v('aadhaarNumber'): aadhaars.add(get_v('aadhaarNumber'))
        if get_v('circle'): circles.add(get_v('circle').upper())

        # Yahan se hum linked numbers uthayenge
        for key in ['mobile', 'alternateNumber']:
            num_val = get_v(key)
            if num_val:
                # Cleaning and filtering
                clean_num = "".join(filter(str.isdigit, num_val))
                if len(clean_num) >= 10 and clean_num != search_num:
                    linked_numbers.add(clean_num)

    # Response build karna
    lines = []
    lines.append("<b>💎 MASTER UNIFIED RECORD</b>")
    lines.append(f"<b>🎯 TARGET:</b> <code>{search_num}</code>")
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    
    # Details (Top unique names and fathers)
    if names: lines.append(f"👤 <b>NAME:</b> <code>{', '.join(list(names)[:3])}</code>") # Top 3 names
    if fathers: lines.append(f"👨‍👦 <b>FATHER:</b> <code>{', '.join(list(fathers)[:3])}</code>")
    if aadhaars: lines.append(f"🆔 <b>AADHAAR:</b> <code>{', '.join(aadhaars)}</code>")
    if circles: lines.append(f"🌍 <b>CIRCLE:</b> <code>{', '.join(circles)}</code>")
    
    # ALT NUMBERS - Ye wahi hai jo aapko chahiye tha
    lines.append("\n📞 <b>ALT NUMBERS (Tap to Copy):</b>")
    if linked_numbers:
        # Har number ko alag se click-to-copy banana
        copy_friendly_list = [f"<code>{n}</code>" for n in sorted(linked_numbers)]
        lines.append(f"┗━━» {', '.join(copy_friendly_list)}")
    else:
        lines.append("┗━━» <i>No alternative numbers found.</i>")

    # Address Section (Ek hi record mein short dikhane ke liye top 2)
    if addresses:
        lines.append("\n🏠 <b>TOP ADDRESSES:</b>")
        for addr in list(addresses)[:2]:
            lines.append(f"┗» <i>{addr}</i>")
    
    lines.append("⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
    return "\n".join(lines)

# --- BOT HANDLERS ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(" ", "").replace("+91", "")
    if not text.isdigit() or len(text) < 10:
        await update.message.reply_html("<b>⚠️ Sahi number bhejien.</b>")
        return

    wait = await update.message.reply_html("<b>⚡ Fetching & Merging all records...</b>")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{text}", timeout=20) as response:
                if response.status == 200:
                    json_res = await response.json()
                    records = json_res.get("data", [])
                    
                    if not records:
                        await wait.edit_text("<b>❌ No Record Found.</b>")
                        return

                    # Poore data ko ek hi msg mein merge karna
                    final_msg = format_single_master_record(records, text)
                    await wait.edit_text(final_msg, parse_mode='HTML')
                else:
                    await wait.edit_text(f"<b>❌ API ERROR:</b> {response.status}")
    except Exception as e:
        await wait.edit_text(f"<b>❌ Error:</b> Connection issue.")

def main():
    keep_alive()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", lambda u,c: u.message.reply_html("<b>Number bhejein!</b>")))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.run_polling()

if __name__ == '__main__':
    main()
    
