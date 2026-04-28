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
    """Faltu symbols hatane aur clean text return karne ke liye"""
    if text is None or str(text).lower() in ['none', 'null', '', ' ']:
        return ""
    # Address ke '!' ko space se replace karna aur trim karna
    return str(text).replace('!', ' ').strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 **Number Search Bot (Optimized)**\n\nBas mobile number bhejiye, main saare linked records merge karke dikha dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_num = update.message.text.strip()
    
    if not query_num.isdigit():
        await update.message.reply_text("❌ Kripya valid digits bhejiye.")
        return

    wait_msg = await update.message.reply_text("Merging data from API... ⏳")
    api_url = f"http://nv6.ek4nsh.in/api/proxy?num={query_num}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        results = data.get("results", [])

        if not results:
            await wait_msg.edit_text("❌ Koi record nahi mila.")
            return

        # Yahan data group hoga Name + Father Name ke hisab se
        merged_records = {}

        for item in results:
            # API Mapping ke hisab se keys (Lowercase)
            name = clean_text(item.get("name")).upper()
            fname = clean_text(item.get("fname")).upper()
            
            if not name: continue # Agar name hi nahi hai toh ignore karein

            # Unique key for merging
            person_key = f"{name}|{fname}"

            # Numbers processing
            raw_mob = clean_text(item.get("mobile"))
            raw_alt = clean_text(item.get("alt"))
            
            current_nums = set()
            for val in [raw_mob, raw_alt]:
                digit_only = re.sub(r'\D', '', val)
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
                    "linked_numbers": current_nums
                }
            else:
                # Purane record mein naye unique numbers add karna
                merged_records[person_key]["linked_numbers"].update(current_nums)
                # Agar koi field pehle khali thi toh use fill karna
                if not merged_records[person_key]["address"]:
                    merged_records[person_key]["address"] = clean_text(item.get("address"))
                if not merged_records[person_key]["id"]:
                    merged_records[person_key]["id"] = clean_text(item.get("id"))
                if not merged_records[person_key]["email"]:
                    merged_records[person_key]["email"] = clean_text(item.get("email"))

        # Final Formatting
        final_output = f"📑 **Search Results for:** `{query_num}`\n"
        final_output += "────────────────────\n"

        for p in merged_records.values():
            all_nums = ", ".join([f"`{n}`" for n in p["linked_numbers"]]) if p["linked_numbers"] else "`Not Found`"
            
            info_block = (
                f"👤 **Name:** `{p['name']}`\n"
                f"👨 **Father:** `{p['fname'] or 'N/A'}`\n"
                f"📍 **Address:** `{p['address'] or 'N/A'}`\n"
                f"📡 **Circle:** `{p['circle'] or 'N/A'}`\n"
                f"🆔 **ID/Aadhar:** `{p['id'] or 'N/A'}`\n"
                f"📧 **Email:** `{p['email'] or 'N/A'}`\n"
                f"🔢 **All Linked Nos:** {all_nums}\n"
                f"────────────────────\n"
            )

            # Check if message length exceeds limit
            if len(final_output) + len(info_block) > 4000:
                await update.message.reply_text(final_output, parse_mode=ParseMode.MARKDOWN)
                final_output = info_block
            else:
                final_output += info_block

        await wait_msg.delete()
        await update.message.reply_text(final_output, parse_mode=ParseMode.MARK
        
