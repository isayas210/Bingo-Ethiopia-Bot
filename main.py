import os
import telebot
from flask import Flask
from threading import Thread

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. WEB SERVER (Render akka hin rafneef)
@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Live!"

# 3. BOT COMMANDS
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Baga Gammaddan! Bot Bingo Ethiopia kallaattiin hojjechaa jira.")

@bot.message_handler(commands=['deposit'])
def deposit(message):
    bot.send_message(message.chat.id, "Kaffaltii CBE: 1000xxxxxx irratti raawwadhaa.")

# 4. BOT RUNNER (Thread keessatti)
def run_bot():
    bot.infinity_polling(non_stop=True)

# 5. MAIN EXECUTION
if __name__ == "__main__":
    # Bot-icha thread addaatiin jalqabsiisuu
    t = Thread(target=run_bot)
    t.start()
    
    # Flask port Render irraa fudhata
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
