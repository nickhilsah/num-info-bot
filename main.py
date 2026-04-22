import logging
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Mobile number bhejiye, main saare records merge karke ek sath dikha dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = update.message.text.strip()
    
    if not num.isdigit() or len(num) < 10:
        await update.message.reply_text("❌ Galat number! Kripya 10-digit mobile number bhejiye.")
        return

    wait_msg = await update.message.reply_text("Searching and Merging Records... ⏳")
    
    api_url = f"http://nv6.ek4nsh.in/api/proxy?num={num}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        results = data.get("results", [])

        if not results:
            await wait_msg.edit_text("info: Koi data nahi mila.")
            return

        # --- Merging & Filtering Logic ---
        merged_data = {}

        for item in results:
            # Cleaning names for better matching
            raw_name = str(item.get("NAME", "UNKNOWN")).strip().upper()
            raw_fname = str(item.get("fname", "UNKNOWN")).strip().upper()
            
            # Unique key based on Name + Father Name
            user_id = f"{raw_name}|{raw_fname}"

            # Aadhaar Masking for Privacy (as per safety guidelines)
            aadhar_val = item.get("id")
            aadhar_display = f"`[Aadhaar Redacted]`" if aadhar_val and str(aadhar_val).strip() != "None" else "`None`"

            # Formatting Address
            addr = str(item.get("ADDRESS", "N/A")).replace("!", " ").strip()
            
            # Collecting Numbers
            primary_mob = str(item.get("MOBILE", "")).strip()
            alt_val = str(item.get("alt", "")).strip()
            
            # If user not in dictionary, add them
            if user_id not in merged_data:
                merged_data[user_id] = {
                    "name": raw_name,
                    "fname": raw_fname,
                    "address": addr,
                    "circle": item.get("circle", "N/A"),
                    "email": item.get("email", "None"),
                    "aadhar": aadhar_display,
                    "numbers": {primary_mob} # Set for unique numbers
                }
                if alt_val and alt_val.lower() != "none" and not alt_val.isalpha():
                    merged_data[user_id]["numbers"].add(alt_val)
            else:
                # If user exists, just update their numbers set
                merged_data[user_id]["numbers"].add(primary_mob)
                if alt_val and alt_val.lower() != "none" and not alt_val.isalpha():
                    merged_data[user_id]["numbers"].add(alt_val)

        # --- Final Message Construction ---
        final_text = f"📑 **Consolidated Records for:** `{num}`\n"
        final_text += "────────────────────\n"

        for uid, info in merged_data.items():
            # Join all unique numbers found for this person
            all_nums = ", ".join([f"`{n}`" for n in info["numbers"] if n])
            
            record_block = (
                f"👤 **Name:** `{info['name']}`\n"
                f"👨 **Father:** `{info['fname']}`\n"
                f"📍 **Address:** `{info['address']}`\n"
                f"📡 **Circle:** `{info['circle']}`\n"
                f"🆔 **Aadhar:** {info['aadhar']}\n"
                f"📧 **Email:** `{info['email']}`\n"
                f"📱 **All Linked Nos:** {all_nums}\n"
                f"────────────────────\n"
            )
            
            # Telegram message limit check
            if len(final_text) + len(record_block) > 4000:
                await update.message.reply_text(final_text, parse_mode=ParseMode.MARKDOWN)
                final_text = record_block
            else:
                final_text += record_block

        await wait_msg.delete()
        await update.message.reply_text(final_text, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(f"Error: {e}")
        await wait_msg.edit_text("⚠️ API se data nikalne me dikkat aa rahi hai.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
    
