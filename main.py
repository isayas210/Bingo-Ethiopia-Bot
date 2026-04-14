import os
import telebot
from flask import Flask, request

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# URL Render keetii (Fkn: https://bingo-ethiopia.onrender.com)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. WEB APP (HTML/JS - Waan hundaa asitti dabarsi)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bingo Ethiopia Mini App</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; text-align: center; background: #001f3f; color: white; margin-top: 50px; }
            .card { background: #003366; padding: 20px; border-radius: 10px; margin: 20px; }
            .btn { background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; width: 80%; }
        </style>
    </head>
    <body>
        <h1>Bingo Ethiopia</h1>
        <div class="card">
            <p>Baga nagaan dhuftan!</p>
            <p>Taphni Bingo fi Kaffaltiin asitti raawwatama.</p>
            <button class="btn" onclick="window.Telegram.WebApp.close()">Taphachiisi</button>
        </div>
    </body>
    </html>
    """

# 3. BOT LOGIC (Nagaa qofa kan gaafatu)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Mini App banuuf button qopheessuu
    web_info = telebot.types.WebAppInfo(url=RENDER_URL)
    button = telebot.types.KeyboardButton(text="🎮 Bingo Tapha Jalqabi", web_app=web_info)
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bot Bingo Ethiopia isa jalqabaati.\n\nTapha jalqabuuf button gadii cuqaasaa.", 
        reply_markup=markup
    )

# 4. WEBHOOK (Render irratti amansiisaa kan ta'e)
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Webhook set successfully!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
