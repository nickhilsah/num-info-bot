import logging
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mobile number bhejiye details nikalne ke liye.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = update.message.text.strip()
    
    if not num.isdigit() or len(num) < 10:
        await update.message.reply_text("Valid 10-digit mobile number bhejiye.")
        return

    wait_msg = await update.message.reply_text("Searching details... 🔍")
    
    api_url = f"http://nv6.ek4nsh.in/api/proxy?num={num}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        results = data.get("results", [])

        if not results:
            await wait_msg.edit_text("Koi details nahi mili.")
            return

        # Data Mapping & Merging Logic
        unique_users = {}

        for item in results:
            # Name aur Father Name ko key banakar duplicates handle karenge
            name = str(item.get("NAME", "N/A")).strip().upper()
            fname = str(item.get("fname", "N/A")).strip().upper()
            user_key = f"{name}_{fname}"

            alt_num = item.get("alt")
            alt_list = [alt_num] if alt_num and alt_num.strip() else []

            if user_key not in unique_users:
                unique_users[user_key] = {
                    "name": name,
                    "father": fname,
                    "address": str(item.get("ADDRESS", "N/A")).replace("!", " "),
                    "circle": item.get("circle", "N/A"),
                    "mobile": item.get("MOBILE", "N/A"),
                    "id": item.get("id", "N/A"),
                    "email": item.get("email", "N/A"),
                    "alternates": set(alt_list)
                }
            else:
                # Agar user pehle se hai toh sirf naya alternate number add karo
                if alt_list:
                    unique_users[user_key]["alternates"].update(alt_list)

        # Message Formatting
        final_response = f"🔍 **Results for:** `{num}`\n\n"
        
        for key, user in unique_users.items():
            alts = ", ".join([f"`{a}`" for a in user["alternates"]]) if user["alternates"] else "N/A"
            
            user_msg = (
                f"👤 **Name:** `{user['name']}`\n"
                f"👨 **Father:** `{user['father']}`\n"
                f"📍 **Address:** `{user['address']}`\n"
                f"📡 **Circle:** `{user['circle']}`\n"
                f"📱 **Mobile:** `{user['mobile']}`\n"
                f"🆔 **ID/Aadhar:** `{user['id']}`\n"
                f"📧 **Email:** `{user['email']}`\n"
                f"🔢 **Alt Nos:** {alts}\n"
                f"────────────────────\n"
            )
            # Telegram ki limit 4096 characters hai, check karein
            if len(final_response) + len(user_msg) > 4000:
                await update.message.reply_text(final_response, parse_mode=ParseMode.MARKDOWN)
                final_response = user_msg
            else:
                final_response += user_msg

        await wait_msg.delete()
        await update.message.reply_text(final_response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logging.error(e)
        await wait_msg.edit_text("API connection error ya data processing me issue hai.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    application.run_polling()
    
