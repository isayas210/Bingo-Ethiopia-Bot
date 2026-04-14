import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Live and Ready!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE SIRRII TA'UU MIRKANEESSI ---
TOKEN = '8798879670:AAGx_YvK1IlF21SQBmjtOmtEpDu7awheG00' 
bot = telebot.TeleBot(TOKEN)

# Yommuu /start jedhamu Button fiduuf
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🎮 Tapha Jalqabi')
    itembtn2 = types.KeyboardButton('📜 Seera Taphaa')
    itembtn3 = types.KeyboardButton('🏆 Sadarkaa (Leaderboard)')
    markup.add(itembtn1, itembtn2, itembtn3)
    
    welcome_text = (
        "🎰 **Baga Gammaddan!**\n\n"
        "Botiin Bingo Ethiopia hojii eegaleera. Maal gochuu barbaaddu?"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# Button-ni yommuu dhiibamu deebii kennuuf
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '🎮 Tapha Jalqabi':
        bot.reply_to(message, "🎲 Qophiidhaa? Kaardiin Bingo keessan qophaa'aa jira...")
    elif message.text == '📜 Seera Taphaa':
        bot.reply_to(message, "📖 Seerri taphaa: Lakkoofsota botiin waamu kaardii kee irratti yoo argatte kallaattiin 'BINGO' jedhi!")
    elif message.text == '🏆 Sadarkaa (Leaderboard)':
        bot.reply_to(message, "📊 Ammaaf hamma taphni jalqabutti sadarkaan hin jiru.")
    else:
        bot.reply_to(message, "Maaloo filannoowwan gadii fayyadamaa.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
