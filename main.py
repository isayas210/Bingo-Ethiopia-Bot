import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# URL Render keetii ofumaan dubbisa
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. MINI APP INTERFACE (Deposit, Withdraw, Bingo)
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
            body { font-family: sans-serif; background-color: #001f3f; color: white; text-align: center; padding: 20px; }
            .card { background-color: #003366; padding: 25px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #007bff; }
            h1 { color: #ffcc00; margin-bottom: 5px; }
            .btn { background-color: #007bff; border: none; color: white; padding: 15px; border-radius: 10px; font-size: 16px; cursor: pointer; width: 100%; margin: 10px 0; font-weight: bold; }
            .btn-bingo { background-color: #28a745; font-size: 20px; }
            .wallet-info { font-size: 14px; color: #00d4ff; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Bingo Ethiopia</h1>
            <p style="font-size: 12px;">Blues Coffee & Sports Betting</p>
            <hr border="0.5">
            <div class="wallet-info">Balance: 0.00 ETB</div>
            
            <button class="btn btn-bingo" onclick="alert('Tapha Bingo Jalqabaa... (Ticket Selection: 1-100)')">🎮 BINGO TAPHA JALQABI</button>
            <button class="btn" onclick="alert('CBE: 1000xxxxxxxxx\\nCBE Birr: 09xxxxxxxx\\nScreenshot kallaattiin bot-itti ergaa.')">💰 DEPOSIT (Maallaqa Galchi)</button>
            <button class="btn" onclick="alert('Withdraw gochuuf herrega keessa ETB 50 gahuu qaba.')">🏦 WITHDRAW (Baasi)</button>
        </div>
        <script>window.Telegram.WebApp.expand();</script>
    </body>
    </html>
    """

# 3. BOT LOGIC (Nagaa qofa kan gaafatu)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = WebAppInfo(url=RENDER_URL)
    button = KeyboardButton(text="🎮 BINGO & WALLET BANI", web_app=web_app)
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bot Bingo Ethiopia isa jalqabaati.\n\nTapha jalqabuuf, kaffaltii raawwachuu fi mo'aticha hordofuuf button gadii fayyadamaa.", 
        reply_markup=markup
    )

# 4. WEBHOOK SETUP
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Forbidden", 403

@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Webhook set successfully!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
