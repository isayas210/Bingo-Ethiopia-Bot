import os
import telebot
from flask import Flask
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# URL Mini App keetii (Render URL kee asitti galchi)
# Fkn: https://bingo-ethiopia.onrender.com
WEB_APP_URL = "https://" + os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')

# 2. WEB SERVER (Inni kun Mini App kee akka banamu godha)
@app.route('/')
def home():
    # Asitti koodii HTML/JS tapha Bingo keetii kanaan duraa galchuu dandeessa
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bingo Ethiopia Mini App</title>
        <style>
            body { font-family: sans-serif; text-align: center; background: #001f3f; color: white; }
            .btn { background: #007bff; color: white; padding: 15px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Bingo Ethiopia</h1>
        <p>Baga nagaan dhuftan! Mini App keessatti tapha keessan hordofaa.</p>
        <button class="btn" onclick="window.Telegram.WebApp.close()">Gara Bot Deebi'i</button>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </body>
    </html>
    """

# 3. BOT COMMAND (Nagaa qofa kan gaafatu)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Button Mini App banu qopheessuu
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = WebAppInfo(url=WEB_APP_URL)
    button = KeyboardButton(text="🎮 Tapha Jalqabi (Mini App)", web_app=web_app)
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bot Bingo Ethiopia isa jalqabaati.\n\nTapha jalqabuuf button gadii cuqaasaa.", 
        reply_markup=markup
    )

# 4. RUNNER
def run_bot():
    bot.infinity_polling(non_stop=True)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
