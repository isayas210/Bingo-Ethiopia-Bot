import os
from flask import Flask
from threading import Thread
import telebot

# --- KAN RENDER IRRATTI BARBAACHISU ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live!"

def run():
    # Render 'PORT' jedhee waan siif kennuuf isuma fayyadamna
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

# Asii gadi 'Code' kee isa duraa itti fufi...
API_TOKEN = os.environ.get('BOT_TOKEN') # Token kee asitti galchi
bot = telebot.TeleBot(API_TOKEN)

# ... (loojikii Bingo kee hunda as galchi) ...

if __name__ == "__main__":
    keep_alive() # Flask jalqabsiisa
    print("Bot is starting...")
    bot.infinity_polling()
