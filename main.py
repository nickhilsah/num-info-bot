import telebot
import requests

# --- CONFIGURATION ---
BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"
# Yahan API link bina "9876543210" ke daalein
API_URL = "https://nv3.ek4nsh.in/api/lookup?term="

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    welcome = (
        "<b>💎 ——— NUMBER LOOKUP BOT ——— 💎</b>\n\n"
        "Bhai, 10 digit number bhejo, details mil jayengi.\n\n"
        "<b>Example:</b> <code>7541951555</code>"
    )
    bot.reply_to(message, welcome, parse_mode="HTML")

@bot.message_handler(func=lambda m: True)
def handle_num(message):
    num = message.text.strip().replace(" ", "").replace("+91", "")

    if not num.isdigit() or len(num) < 10:
        bot.reply_to(message, "<b>⚠️ ERROR:</b> 10-digit number dalo bhai.")
        return

    loading = bot.reply_to(message, "<b>⚡ Searching Database...</b>", parse_mode="HTML")

    try:
        # API Call
        full_url = f"{API_URL}{num}"
        r = requests.get(full_url, timeout=15)
        
        # Terminal mein check karo kya aa raha hai
        print(f"Status Code: {r.status_code}")
        print(f"Full Response: {r.text}")

        data = r.json()

        # Agar data list hai [ {...} ], toh pehla item nikalo
        if isinstance(data, list) and len(data) > 0:
            info = data[0]
        elif isinstance(data, dict):
            info = data
        else:
            info = None

        if info:
            # Keys ko proper extract karein
            name = str(info.get("name", "N/A")).upper()
            f_name = str(info.get("fatherName", "N/A")).upper()
            addr = str(info.get("address", "N/A")).upper()
            circle = str(info.get("circle", "N/A")).upper()
            adhar = str(info.get("aadhaarNumber", "N/A"))

            # Premium Bold Layout with Emojis
            result = (
                "<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n\n"
                f"<b>📱 TARGET :</b> <code>{num}</code>\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
                f"👤 <b>NAME</b>\n┗━━» <b>{name}</b>\n\n"
                f"👨‍👦 <b>FATHER NAME</b>\n┗━━» <b>{f_name}</b>\n\n"
                f"🌍 <b>CIRCLE</b>\n┗━━» <b>{circle}</b>\n\n"
                f"🏠 <b>ADDRESS</b>\n┗━━» <b>{addr}</b>\n\n"
                f"🆔 <b>AADHAAR NO</b>\n┗━━» <code>{adhar}</code>\n\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                "<b>✅ DATA FETCHED SUCCESSFULLY</b>"
            )
            bot.edit_message_text(result, message.chat.id, loading.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("<b>❌ NO RECORD FOUND</b>\nAPI ke paas is number ka data nahi hai.", message.chat.id, loading.message_id, parse_mode="HTML")

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(f"<b>❌ ERROR:</b> <code>{str(e)}</code>", message.chat.id, loading.message_id, parse_mode="HTML")

if __name__ == "__main__":
    print("🤖 Bot Running...")
    bot.infinity_polling()
