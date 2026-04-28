import logging
import requests
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"

def clean_text(text):
    """Faltu symbols hatane ke liye helper"""
    if text is None or str(text).lower() in ['none', 'null', '', ' ']:
        return ""
    return str(text).replace('!', ' ').strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bot ke "What can this bot do?" section jaisa message
    start_text = (
        "🤖 **Welcome to Multi-Lookup Bot!**\n"
        "🚀 **Created by Nikhil**\n\n"
        "📞 Phone - Mobile number lookup\n"
        "🆔 Aadhaar - Aadhaar information\n"
        "🏦 IFSC - Bank branch details\n"
        "🚗 Vehicle - Vehicle RC details\n\n"
        "__Enter 10 digit number__"
    )
    await update.message.reply_text(start_text, parse_mode=ParseMode.MARKDOWN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_num = update.message.text.strip()
    
    if not query_num.isdigit() or len(query_num) < 10:
        await update.message.reply_text("❌ Kripya sahi 10-digit mobile number bhejiye.")
        return

    wait_msg = await update.message.reply_text("Searching details... 🔍")
    api_url = f"http://nv6.ek4nsh.in/api/proxy?num={query_num}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        results = data.get("results", [])

        if not results:
            await wait_msg.edit_text("❌ Koi record nahi mila.")
            return

        # Merging Logic (Name + Father Name ke basis par)
        merged_records = {}

        for item in results:
            # Aapke naye mapping ke hisab se keys (mobile, name, fname, id, etc.)
            name = clean_text(item.get("name")).upper()
            fname = clean_text(item.get("fname")).upper()
            
            if not name: continue

            person_key = f"{name}|{fname}"

            # Mobile aur Alt numbers collect karna
            current_nums = set()
            for key in ["mobile", "alt"]:
                val = clean_text(item.get(key))
                digit_only = re.sub(r'\D', '', val) # Sirf numbers rakho
                if len(digit_only) >= 10:
                    current_nums.add(digit_only)

            if person_key not in merged_records:
                merged_records[person_key] = {
                    "name": name,
                    "fname": fname,
                    "address": clean_text(item.get("address")),
                    "circle": clean_text(item.get("circle")),
                    "id": clean_text(item.get("id")),
                    "email": clean_text(item.get("email")),
                    "linked_nums": current_nums
                }
            else:
                # Agar banda same hai toh naye numbers aur missing info add karo
                merged_records[person_key]["linked_nums"].update(current_nums)
                if not merged_records[person_key]["address"]:
                    merged_records[person_key]["address"] = clean_text(item.get("address"))
                if not merged_records[person_key]["id"]:
                    merged_records[person_key]["id"] = clean_text(item.get("id"))
                if not merged_records[person_key]["email"]:
                    merged_records[person_key]["email"] = clean_text(item.get("email"))

        # Message Formatting
        final_output = f"🔍 **Results for:** `{query_num}`\n"
        final_output += "────────────────────\n"

        for p in merged_records.values():
            # Saare numbers ek sath merge hokar dikhenge
            nums_str = ", ".join([f"`{n}`" for n in p["linked_nums"]]) if p["linked_numbers"] else "`N/A`"
            
            info_block = (
                f"👤 **Name:** `{p['name']}`\n"
                f"👨 **Father:** `{p['fname'] or 'N/A'}`\n"
                f"📍 **Address:** `{p['address'] or 'N/A'}`\n"
                f"📡 **Circle:** `{p['circle'] or 'N/A'}`\n"
                f"🆔 **ID/Aadhar:** `{p['id'] or 'N/A'}`\n"
                f"📧 **Email:** `{p['email'] or 'N/A'}`\n"
                f"🔢 **Alt/Linked Nos:** {nums_str}\n"
                f"────────────────────\n"
            )

            if len(final_output) + len(info_block) > 4000:
                await update.message.reply_text(final_output, parse_mode=ParseMode.MARKDOWN)
                final_output = info_block
            else:
                final_output += info_block

        await wait_msg.delete()
        await update.message.reply_text(final_output, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error: {e}")
        await wait_msg.edit_text("⚠️ API error ya data processing issue.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
    
