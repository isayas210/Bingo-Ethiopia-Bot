
import telebot
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Botiin kee hojii irratti jira!"

def run():
    # Render port kallaattiin akka banamu gargaara
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE KANA JALATTI GALCHI ---
TOKEN = '7611593340:AAEO6n_DIn9lE3-j6K7yv288l756N1-0Wc' # Token kee asitti galchi
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Baga gammadde! Botiin Bingo Ethiopia Render irratti hojii eegaleera. 🎰")

if __name__ == "__main__":
    keep_alive() # Port akka banamu godha
    bot.infinity_polling()
