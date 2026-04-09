import telebot
import requests

BOT_TOKEN = "8651545654:AAGGuLV625bR3NuQh_ixgfrKM3FtFCZPPPQ"

API_URL = "https://nv3.ek4nsh.in/api/lookup?term=9876543210"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    welcome = (
        "🔍 *Number Info Bot Activated!*\n\n"
        "Mujhe koi bhi 10 digit Indian mobile number bhejo.\n"
        "Main uski details fetch kar dunga.\n\n"
        "Example: `9876543210`"
    )
    bot.reply_to(message, welcome, parse_mode="Markdown")


@bot.message_handler(func=lambda m: True)
def handle_num(message):
    num = message.text.strip().replace(" ", "").replace("+91", "")

    if not num.isdigit() or len(num) != 10:
        bot.reply_to(message, "❌ *Invalid Number!*", parse_mode="Markdown")
        return

    loading = bot.reply_to(message, "🔄 *Fetching information...*", parse_mode="Markdown")

    try:
        url = API_URL.format(mob=num, key=API_KEY)
        r = requests.get(url, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text("❌ Server error.", message.chat.id, loading.message_id)
            return

        data = r.json()

        if data.get("valid") is True:
            
            operator = data.get("carrier", "N/A")
            circle = data.get("location", "N/A")
            address = data.get("location", "N/A")   # address = location

            result = (
                "✅ *Details Found!*\n\n"
                f"📱 Number: `{num}`\n"
                f"📡 Carrier: `{operator}`\n"
                f"🌍 Circle: `{circle}`\n"
                f"🏙 City: `{circle}`\n"
                f"⚠️ Address: `{address}`\n"
            )

            bot.edit_message_text(result, message.chat.id, loading.message_id, parse_mode="Markdown")

        else:
            bot.edit_message_text("❌ No data found.", message.chat.id, loading.message_id)

    except:
        bot.edit_message_text("❌ Unexpected error.", message.chat.id, loading.message_id)


print("🤖 Bot Running...")
bot.infinity_polling(none_stop=True)

