import os
import telebot
from flask import Flask
import threading

# 1. SETUP (Token kee Render irraa dubbisa)
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. WEB SERVER (Render akka hin rafneef)
@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Active!"

# 3. COMMANDS
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Baga Gammaddan! Bot Bingo Ethiopia kallaattiin hojjechaa jira.\n\n/deposit - Herrega guuttachuuf\n/bingo - Taphachuuf")

@bot.message_handler(commands=['deposit'])
def deposit(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("CBE", callback_data="cbe"))
    markup.add(telebot.types.InlineKeyboardButton("CBE Birr", callback_data="cbe_birr"))
    bot.send_message(message.chat.id, "Akkaataa kaffaltii filadhu:", reply_markup=markup)

# 4. LOGIC (Kaffaltii fi 30% Hir'isuu)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cbe":
        bot.send_message(call.message.chat.id, "Lakk. Herrega CBE: 1000xxxxxxxxx\nErga kaffaltii raawwattanii booda screenshot ergaa.")
    elif call.data == "cbe_birr":
        bot.send_message(call.message.chat.id, "Lakk. CBE Birr: 09xxxxxxxx\nKaffaltii booda screenshot ergaa.")

# 5. WINNING LOGIC (Komishinii 30% ofumaan hir'isuu)
def calculate_payout(amount):
    # 30% commission hir'isuu
    payout = amount * 0.70
    return payout

# 6. RUN BOT (Threading fayyadamuun)
def run_bot():
    print("Bot is starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    # Bot thread addaatiin jalqaba
    threading.Thread(target=run_bot).start()
    # Flask port Render irraa fudhata
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
