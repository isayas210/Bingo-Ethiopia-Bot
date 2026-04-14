import telebot
from flask import Flask
from threading import Thread
import os

# Render akka bota kee hin cufneef kuta kana itti daballa
app = Flask('')

@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Running!"

def run():
    # Port Render irratti barbaadamu
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE KANA JALATTI GALCHI ---
TOKEN = '7611593340:AAEO6n_DIn9lE3-j6K7yv288l756N1-0Wc' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎰 Baga Gammaddan! Botiin Bingo Ethiopia amma guutummaatti hojii eegaleera. 🎰")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Tapha Bingo jalqabuuf /start fayyadamaa.")

if __name__ == "__main__":
    keep_alive()
    print("Bot is alive...")
    bot.infinity_polling()
