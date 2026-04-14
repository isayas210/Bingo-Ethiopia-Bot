import os
import telebot
from flask import Flask

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. WEB SERVER (Render akka hin rafneef)
@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Active!"

# 3. BOT LOGIC
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Baga Gammaddan! Bot Bingo Ethiopia kallaattiin hojjechaa jira.\n\n/deposit - Herrega guuttachuuf\n/bingo - Taphachuuf")

@bot.message_handler(commands=['deposit'])
def deposit(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("CBE", callback_data="cbe"))
    markup.add(telebot.types.InlineKeyboardButton("CBE Birr", callback_data="cbe_birr"))
    bot.send_message(message.chat.id, "Akkaataa kaffaltii filadhu:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cbe":
        bot.send_message(call.message.chat.id, "Lakk. Herrega CBE: 1000xxxxxxxxx\nErga kaffaltii raawwattanii booda screenshot ergaa.")
    elif call.data == "cbe_birr":
        bot.send_message(call.message.chat.id, "Lakk. CBE Birr: 09xxxxxxxx\nKaffaltii booda screenshot ergaa.")

# 4. RENDER IRRATTI AKKA HOJJETU (Webhook malee polling salphaa)
if __name__ == "__main__":
    # Flask port Render irraa fudhata
    port = int(os.environ.get("PORT", 5000))
    
    # Bot-icha kallaattiin jalqabsiisuu
    # None-stop=True akka inni kuffisee hin dhaabbannee gargaara
    print("Bot is starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
