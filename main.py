import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# URL Mini App keetii (Render URL kee kallaattiin fudhata)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. WEB APP (Deposit, Withdraw fi Bingo hunda of keessaa qaba)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia Mini App</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #001f3f; color: white; text-align: center; margin: 0; padding: 20px; }
            .container { background-color: #003366; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            h1 { color: #ffcc00; }
            .menu-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
            .btn { background-color: #007bff; border: none; color: white; padding: 15px; border-radius: 8px; font-size: 16px; cursor: pointer; transition: 0.3s; }
            .btn:hover { background-color: #0056b3; }
            .btn-bingo { grid-column: span 2; background-color: #28a745; font-weight: bold; font-size: 20px; }
            .footer { margin-top: 30px; font-size: 12px; color: #aaa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bingo Ethiopia</h1>
            <p>Baga nagaan dhuftan!</p>
            
            <div class="menu-grid">
                <button class="btn btn-bingo" onclick="alert('Tapha Bingo Jalqabaa...')">🎮 Tapha Jalqabi</button>
                <button class="btn" onclick="alert('CBE: 1000xxxxxx\\nCBE Birr: 09xxxxxxxx')">💰 Deposit</button>
                <button class="btn" onclick="alert('Gatii baasuu (Withdraw) dhiyoo dha...')">🏦 Withdraw</button>
            </div>

            <div class="footer">
                <p>Blues Coffee & Bingo System</p>
            </div>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand(); // Screen guutuu akka ta'uuf
        </script>
    </body>
    </html>
    """

# 3. BOT LOGIC (Nagaa qofa kan gaafatu)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Mini App banuuf button
    web_info = WebAppInfo(url=RENDER_URL)
    button = KeyboardButton(text="🎮 Bingo & Wallet Bani", web_app=web_info)
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bot Bingo Ethiopia isa jalqabaati.\n\nDeposit gochuuf, withdraw fi tapha Bingo hundaaf button gadii fayyadamaa.", 
        reply_markup=markup
    )

# 4. WEBHOOK SETUP
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
