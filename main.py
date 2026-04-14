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

# --- FRONTEND DESIGN (CHELSEA BLUE THEME) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethiopia</title>
    <style>
        body { background: #001489; color: white; font-family: 'Arial', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .container { border: 3px solid #DBA111; border-radius: 20px; padding: 30px; background: rgba(0,0,0,0.7); box-shadow: 0 0 30px #DBA111; }
        h1 { color: #DBA111; font-size: 2.5em; margin-bottom: 10px; }
        .balance-box { font-size: 1.8em; margin: 15px 0; color: #00FF00; font-weight: bold; }
        .play-btn { background: #DBA111; color: #000; border: none; padding: 18px 45px; font-size: 1.3em; font-weight: bold; border-radius: 50px; cursor: pointer; }
        .footer { margin-top: 40px; font-size: 0.9em; color: #ccc; border-top: 1px solid #DBA111; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BINGO ETHIOPIA</h1>
        <div class="balance-box">💰 Balance: 10 ETB</div>
        <button class="play-btn" onclick="alert('Botiin keessan Telegram irratti kaardii isiniif ergeera. Gara Bot keessanii deebi'aa!')">TAPHA JALQABI</button>
        <div class="footer">Madda Walabu University | Mechanical Engineering</div>
    </div>
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
    bot.send_message(message.chat.id, "🎰 **Baga Gammaddan!**\nBingo Ethiopia haala haaraan qophaa'ee dhufeera.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    if message.text == '🎮 Tapha Jalqabi':
        if user_balances.get(user_id, 0) < 10:
            bot.reply_to(message, "⚠️ Qarshiin keessan gahaa miti. Maaloo 💳 Deposit dhiibaa.")
        else:
            user_balances[user_id] -= 10
            card = generate_bingo_card()
            bot.send_message(message.chat.id, f"🎲 **Kaardii Keessan:**\n\n" + format_card(card), parse_mode='MarkdownV2')
            
            # Draw 5 random numbers automatically
            drawn = random.sample(range(1, 76), 5)
            game_numbers[user_id] = drawn
            bot.send_message(message.chat.id, "🔢 **Lakkoofsota Waamaman:**")
            for n in drawn:
                time.sleep(2)
                bot.send_message(message.chat.id, f"👉 **{n}**", parse_mode='Markdown')
            
            bot.send_message(message.chat.id, "💡 Yoo kaardii keessan guuttan **'BINGO'** jedhaatii barreessaa!")

    elif message.text.upper() == 'BINGO':
        if user_id in game_numbers:
            user_balances[user_id] += 50
            bot.send_message(message.chat.id, "🎉 **BINGO!** 🎉\nInjifannoon keessan mirkanaa'eera. 50 ETB account keessanitti dabalameera!")
            del game_numbers[user_id]
        else:
            bot.send_message(message.chat.id, "❌ Maaloo dursa tapha jalqabaa!")

    elif message.text == '💰 Balance Ko':
        bot.reply_to(message, f"💵 Qarshiin keessan: **{user_balances.get(user_id, 0)} ETB**")

    elif message.text == '💳 Deposit':
        user_balances[user_id] = user_balances.get(user_id, 0) + 50
        bot.reply_to(message, "✅ Qarshii 50 account keessanitti dabalameera!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
