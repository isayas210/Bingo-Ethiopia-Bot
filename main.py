import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import random
import time

app = Flask('')

@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c' 
bot = telebot.TeleBot(TOKEN)

# --- DATABASE SALPHAA ---
user_balances = {}

def get_balance(user_id):
    return user_balances.get(user_id, 0)

def update_balance(user_id, amount):
    user_balances[user_id] = get_balance(user_id) + amount

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
    
    # --- NAMNI HAARAA YOO TA'E QARSHII 10 KENNI ---
    if user_id not in user_balances:
        user_balances[user_id] = 10
        welcome_text = "🎰 **Baga Gammaddan!**\n\nKennaa jalqabaa **10 ETB** account keessanitti dabaleera! 🎁"
    else:
        welcome_text = "🎰 **Bingo Ethiopia**-tti deebitanii baga gammaddan!"

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🎮 Tapha Jalqabi')
    itembtn2 = types.KeyboardButton('💰 Balance Ko')
    itembtn3 = types.KeyboardButton('💳 Deposit')
    itembtn4 = types.KeyboardButton('📜 Seera Taphaa')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    if message.text == '🎮 Tapha Jalqabi':
        current_bal = get_balance(user_id)
        if current_bal < 10:
            bot.reply_to(message, "⚠️ Balance keessan gahaa miti. Maaloo dursa Deposit godhaa.")
        else:
            update_balance(user_id, -10)
            card = generate_bingo_card()
            bot.send_message(message.chat.id, f"🎲 Kunoo Kaardii keessan:\n(Balance hafe: {get_balance(user_id)} ETB)\n\n" + format_card(card), parse_mode='MarkdownV2')
            
    elif message.text == '💰 Balance Ko':
        bal = get_balance(user_id)
        bot.reply_to(message, f"💵 Qarshiin keessan: **{bal} ETB**", parse_mode='Markdown')
        
    elif message.text == '💳 Deposit':
        update_balance(user_id, 50)
        bot.reply_to(message, "✅ Qarshii 50 account keetti dabalameera!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
