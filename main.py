import logging
import requests
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"

def format_clean(text):
    """Faltu symbols aur extra spaces hatane ke liye"""
    if not text or str(text).lower() in ['none', 'null', 'nan', '', ' ']:
        return ""
    # Address se '!' hatakar space dena aur extra spaces trim karna
    return str(text).replace('!', ' ').strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 **Number Search Bot Optimized**\n\nMobile number bhejiye, main saare records merge karke dikha dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_num = update.message.text.strip()
    
    if not query_num.isdigit():
        await update.message.reply_text("❌ Kripya sirf digits (number) bhejiye.")
        return

    wait_msg = await update.message.reply_text("Searching & Merging Data... ⏳")
    api_url = f"http://nv6.ek4nsh.in/api/proxy?num={query_num}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        results = data.get("results", [])

        if not results:
            await wait_msg.edit_text("❌ Koi record nahi mila.")
            return

        unique_data = {}

        for item in results:
            # Safai (Cleaning)
            name = format_clean(item.get("name") or item.get("NAME")).upper()
            fname = format_clean(item.get("fname")).upper()
            
            # Agar Name aur Father Name dono khali hain toh skip karein
            if not name and not fname: continue

            # Merging Key: Name + Father Name (Isse duplicates merge honge)
            key = f"{name}|{fname}"

            # Number handling (Primary aur Alternate dono)
            mob = format_clean(item.get("mobile") or item.get("MOBILE"))
            alt = format_clean(item.get("alt"))
            
            nums_to_add = set()
            for n in [mob, alt]:
                clean_n = re.sub(r'\D', '', n) # Sirf digits rakhein
                if len(clean_n) >= 10: # Kam se kam 10 digit ka number ho
                    nums_to_add.add(clean_n)

            if key not in unique_data:
                unique_data[key] = {
                    "name": name or "NOT AVAILABLE",
                    "fname": fname or "NOT AVAILABLE",
                    "address": format_clean(item.get("address") or item.get("ADDRESS")),
                    "circle": format_clean(item.get("circle")),
                    "id": format_clean(item.get("id")),
                    "email": format_clean(item.get("email")),
                    "all_nums": nums_to_add
                }
            else:
                # Agar user exists hai, toh bas naye numbers aur fields update karein
                unique_data[key]["all_nums"].update(nums_to_add)
                # Agar pehle email nahi tha aur ab mil gaya
                if not unique_data[key]["email"]:
                    unique_data[key]["email"] = format_clean(item.get("email"))
                if not unique_data[key]["id"]:
                    unique_data[key]["id"] = format_clean(item.get("id"))

        # Message Formatting
        final_msg = f"📑 **Consolidated Results for:** `{query_num}`\n"
        final_msg += "────────────────────\n"

        for person in unique_data.values():
            # Numbers ko tap-to-copy format mein comma se separate karna
            linked_nums = ", ".join([f"`{n}`" for n in person["all_nums"]]) if person["all_nums"] else "`N/A`"
            
            block = (
                f"👤 **Name:** `{person['name']}`\n"
                f"👨 **Father:** `{person['fname']}`\n"
                f"📍 **Address:** `{person['address'] or 'N/A'}`\n"
                f"📡 **Circle:** `{person['circle'] or 'N/A'}`\n"
                f"🆔 **ID/Aadhar:** `{person['id'] or 'N/A'}`\n"
                f"📧 **Email:** `{person['email'] or 'N/A'}`\n"
                f"🔢 **Linked Nos:** {linked_nums}\n"
                f"────────────────────\n"
            )

            if len(final_msg) + len(block) > 4000:
                await update.message.reply_text(final_msg, parse_mode=ParseMode.MARKDOWN)
                final_msg = block
            else:
                final_msg += block

        await wait_msg.delete()
        await update.message.reply_text(final_msg, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error: {e}")
        await wait_msg.edit_text("⚠️ Data fetch karne mein error aaya. API check karein.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
    
