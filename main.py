import telebot
from telebot import types
from flask import Flask, render_template_string
from threading import Thread
import os
import random

app = Flask('')

# --- DATABASE SALPHAA ---
user_balances = {}

# --- HTML/CSS (Bareeda Mini App) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethiopia</title>
    <style>
        body { background: radial-gradient(circle, #1a1a2e, #16213e); color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { border: 2px solid #f1c40f; border-radius: 20px; padding: 30px; background: rgba(0,0,0,0.5); box-shadow: 0 0 20px #f1c40f; }
        h1 { color: #f1c40f; text-shadow: 2px 2px #000; font-size: 2.5em; }
        .balance-box { font-size: 1.5em; margin: 20px 0; color: #2ecc71; }
        .play-btn { background: #f1c40f; color: #000; border: none; padding: 15px 40px; font-size: 1.2em; font-weight: bold; border-radius: 50px; cursor: pointer; transition: 0.3s; }
        .play-btn:hover { transform: scale(1.1); background: #fff; }
        .footer { margin-top: 30px; font-size: 0.8em; color: #bdc3c7; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BINGO ETHIOPIA</h1>
        <div class="balance-box">💰 Balance: <b>10 ETB</b></div>
        <button class="play-btn" onclick="tgAlert()">TAPHA JALQABI</button>
        <div class="footer">Madda Walabu University Bot Development</div>
    </div>
    <script>
        function tgAlert() {
            alert("Botiin keessan Telegram irratti Kaardii siif ergaa jira. Bot kee ilaali!");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE ---
TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 10
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🎮 Tapha Jalqabi', '💰 Balance Ko', '💳 Deposit', '📜 Seera Taphaa')
    bot.send_message(message.chat.id, "🎰 **Bingo Ethiopia**-tti baga gammadde! Kennaa 10 ETB siif kenneera.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if message.text == '💰 Balance Ko':
        bal = user_balances.get(user_id, 0)
        bot.reply_to(message, f"💵 Qarshiin keessan: **{bal} ETB**")
    elif message.text == '💳 Deposit':
        user_balances[user_id] = user_balances.get(user_id, 0) + 50
        bot.reply_to(message, "✅ Qarshii 50 dabalameera!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
