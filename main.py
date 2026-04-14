import telebot
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Live with New Token!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN HAARAA KANA JALATTI GALCHERA ---
TOKEN = '8798879670:AAGx_YvK1IlF21SQBmjtOmtEpDu7awheG00' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎰 Baga Gammaddan! Botiin Bingo Ethiopia Token haaraa kanaan hojii eegaleera.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Tapha Bingo jalqabuuf /start fayyadamaa.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
