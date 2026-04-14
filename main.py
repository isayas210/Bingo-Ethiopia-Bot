import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import random

app = Flask('')

@app.route('/')
def home():
    return "Bingo Ethiopia Bot is Live and Ready!"

def run():
    # Render port 8080 ykn 10000 fayyadama
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE HAARAA AS JIRA ---
TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c' 
bot = telebot.TeleBot(TOKEN)

# Kaardii Bingo lakkoofsa 25 qabu uumuuf (5x5)
def generate_bingo_card():
    card = []
    # Columns B(1-15), I(16-30), N(31-45), G(46-60), O(61-75)
    ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
    for start, end in ranges:
        column = random.sample(range(start, end + 1), 5)
        card.append(column)
    
    # Gidduu kaardichaa 'FREE' gochuuf
    card[2][2] = "FREE"
    return card

def format_card(card):
    # Kaardicha bifa table-iin qopheessuuf (Code block keessatti)
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
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🎮 Tapha Jalqabi')
    itembtn2 = types.KeyboardButton('📜 Seera Taphaa')
    markup.add(itembtn1, itembtn2)
    
    welcome_msg = (
        "🎰 **Baga Gammaddan!**\n\n"
        "Botiin Bingo Ethiopia haaraa kanaan hojii eegaleera.\n"
        "Kaardii keessan fudhachuuf button gadii dhiibaa."
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '🎮 Tapha Jalqabi':
        card = generate_bingo_card()
        card_text = format_card(card)
        bot.send_message(message.chat.id, "🎲 Kunoo Kaardii keessan:\n\n" + card_text, parse_mode='MarkdownV2')
        bot.send_message(message.chat.id, "Lakkoofsota botiin waamu hordofaa! Yoo guuttan 'BINGO' jedhaa.")
    elif message.text == '📜 Seera Taphaa':
        bot.reply_to(message, "📖 Seera: Kaardii kee irratti sarara (horizontal, vertical, ykn diagonal) tokko yoo guutte kallaattiin 'BINGO' jedhi!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
