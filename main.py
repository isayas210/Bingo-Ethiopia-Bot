import telebot
from flask import Flask, render_template_string
from threading import Thread
import os

# Token kee as galchi
BOT_TOKEN = "7710960579:AAH9mS5Cid_8M37v0xX6-uS_8CA972-c0Xg"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Fuula "Home" Render irratti mul'atu
@app.route('/')
def home():
    # Koodii HTML Telebirr hin qabne
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bingo Ethiopia</title>
        <style>
            body { background-color: #000; color: white; text-align: center; font-family: Arial; padding-top: 50px; }
            h1 { color: #0088cc; }
        </style>
    </head>
    <body>
        <h1>Bingo Ethiopia Is Live!</h1>
        <p>Bot kee sirriitti hojjechaa jira.</p>
    </body>
    </html>
    """

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.polling(none_stop=True)
