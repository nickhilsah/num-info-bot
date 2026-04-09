import telebot
import requests
import logging

# --- CONFIGURATION ---
BOT_TOKEN = "YOUR_BOT_API_TOKEN"
API_BASE_URL = "https://nv3.ek4nsh.in/api/lookup?term="

bot = telebot.TeleBot(BOT_TOKEN)

# Logging setup (Optional but good for debugging)
logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    welcome = (
        "<b>💎 ——— NUMBER LOOKUP BOT ——— 💎</b>\n\n"
        "Bhai, mujhe koi bhi 10 digit Indian number bhejo.\n"
        "Main details nikaal kar ekdum premium style mein dunga!\n\n"
        "<b>Example:</b> <code>9876543210</code>"
    )
    bot.reply_to(message, welcome, parse_mode="HTML")

@bot.message_handler(func=lambda m: True)
def handle_num(message):
    # Number clean up
    num = message.text.strip().replace(" ", "").replace("+91", "")

    if not num.isdigit() or len(num) < 10:
        bot.reply_to(message, "<b>⚠️ ERROR:</b> Sahi 10-digit number dalo bhai.", parse_mode="HTML")
        return

    # Loading message
    loading = bot.reply_to(message, "<b>⚡ Searching Database...</b>", parse_mode="HTML")

    try:
        # API Request
        url = f"{API_BASE_URL}{num}"
        r = requests.get(url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text("<b>❌ SERVER ERROR:</b> API response nahi de rahi.", message.chat.id, loading.message_id, parse_mode="HTML")
            return

        data = r.json()

        # Checking if data exists (handling the list format)
        if isinstance(data, list) and len(data) > 0:
            info = data[0]
            
            # Extracting details with fallback "N/A"
            name = info.get("name", "N/A").upper()
            f_name = info.get("fatherName", "N/A").upper()
            addr = info.get("address", "N/A").upper()
            circle = info.get("circle", "N/A").upper()
            adhar = info.get("aadhaarNumber", "N/A")
            mob = info.get("mobile", num)

            # Premium Bold Formatting with Emojis
            result = (
                "<b>💎 ——— NUMBER DETAILS ——— 💎</b>\n\n"
                f"<b>📱 TARGET :</b> <code>{mob}</code>\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n"
                f"👤 <b>NAME</b>\n┗━━» <code>{name}</code>\n\n"
                f"👨‍👦 <b>FATHER NAME</b>\n┗━━» <code>{f_name}</code>\n\n"
                f"🌍 <b>NETWORK CIRCLE</b>\n┗━━» <code>{circle}</code>\n\n"
                f"🏠 <b>ADDRESS</b>\n┗━━» <code>{addr}</code>\n\n"
                f"🆔 <b>AADHAAR NO</b>\n┗━━» <code>{adhar}</code>\n\n"
                "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                "<b>✅ SUCCESS : DATA FETCHED</b>"
            )

            bot.edit_message_text(result, message.chat.id, loading.message_id, parse_mode="HTML")

        else:
            bot.edit_message_text("<b>❌ NO DATA:</b> Is number ki details nahi mili.", message.chat.id, loading.message_id, parse_mode="HTML")

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("<b>❌ ERROR:</b> Kuch technical issue aa gaya.", message.chat.id, loading.message_id, parse_mode="HTML")


if __name__ == "__main__":
    print("🤖 Bot is running like a pro...")
    bot.infinity_polling()
