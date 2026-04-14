import telebot
from telebot import types
from flask import Flask, render_template_string
from threading import Thread
import os
import random
import time

app = Flask('')

# --- DATABASE SALPHAA ---
user_balances = {}
game_numbers = {} 

# --- FRONTEND DESIGN (CHELSEA BLUE & GOLD) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethiopia</title>
    <style>
        body { background: #001489; color: white; font-family: 'Arial', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { border: 3px solid #DBA111; border-radius: 20px; padding: 30px; background: rgba(0,0,0,0.8); box-shadow: 0 0 30px #DBA111; }
        h1 { color: #DBA111; font-size: 2.5em; margin-bottom: 10px; }
        .balance-box { font-size: 1.8em; margin: 15px 0; color: #00FF00; font-weight: bold; }
        .play-btn { background: #DBA111; color: #000; border: none; padding: 18px 45px; font-size: 1.3em; font-weight: bold; border-radius: 50px; cursor: pointer; width: 100%; }
        .footer { margin-top: 40px; font-size: 0.9em; color: #ccc; border-top: 1px solid #DBA111; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BINGO ETHIOPIA</h1>
        <div class="balance-box">💰 Balance: 10 ETB</div>
        <button class="play-btn" onclick="sendGameRequest()">TAPHA JALQABI</button>
        <div class="footer">Bingo Ethiopia Official Bot</div>
    </div>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        function sendGameRequest() {
            tg.sendData("🎮 Tapha Jalqabi"); // Kallaattiin gara botaatti erga
            tg.close(); // App-icha cufee bota keessa si galcha
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

TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c' 
bot = telebot.TeleBot(TOKEN)

# --- BINGO LOGIC ---
def generate_bingo_card():
    card = []
    ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
    for start, end in ranges:
        column = random.sample(range(start, end + 1), 5)
        card.append(column)
    card[2][2] = "FREE"
    return card

def format_card(card):
    header = " B  | I  | N  | G  | O \n-------------------\n"
    rows = ""
    for i in range(5):
        row = ""
        for j in range(5):
            val = str(card[j][i]).center(3)
            row += f"{val}|"
        rows += row[:-1] + "\n"
    return f"```{header}{rows}```"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 10
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🎮 Tapha Jalqabi', '💰 Balance Ko', '💳 Deposit', '📜 Seera Taphaa')
    bot.send_message(message.chat.id, "🎰 **Baga Gammaddan!**\nTapha jalqabuuf button dhiibaa.", reply_markup=markup, parse_mode='Markdown')

# Mini App irraa ykn kallaattiin Button dhiibamee yoo dhufe
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text

    if text == '🎮 Tapha Jalqabi' or (message.web_app_data and message.web_app_data.data == '🎮 Tapha Jalqabi'):
        if user_balances.get(user_id, 0) < 10:
            bot.send_message(message.chat.id, "⚠️ Balance keessan gahaa miti.")
        else:
            user_balances[user_id] -= 10
            card = generate_bingo_card()
            bot.send_message(message.chat.id, f"🎲 **Kaardii Keessan:**\n\n" + format_card(card), parse_mode='MarkdownV2')
            
            drawn = random.sample(range(1, 76), 5)
            game_numbers[user_id] = drawn
            bot.send_message(message.chat.id, "🔢 **Lakkoofsota Waamaman:**")
            for n in drawn:
                time.sleep(1.5)
                bot.send_message(message.chat.id, f"👉 **{n}**")
            bot.send_message(message.chat.id, "💡 Bingo yoo guuttan 'BINGO' jedhaa.")

    elif text.upper() == 'BINGO':
        if user_id in game_numbers:
            user_balances[user_id] += 50
            bot.send_message(message.chat.id, "🎉 **BINGO!** 50 ETB siif dabalameera.")
            del game_numbers[user_id]
        else:
            bot.send_message(message.chat.id, "❌ Maaloo dursa tapha jalqabi.")

    elif text == '💰 Balance Ko':
        bot.reply_to(message, f"💵 Balance: **{user_balances.get(user_id, 0)} ETB**")

    elif text == '💳 Deposit':
        user_balances[user_id] = user_balances.get(user_id, 0) + 50
        bot.reply_to(message, "✅ 50 ETB dabalameera.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
