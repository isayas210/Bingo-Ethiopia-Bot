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
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- TOKEN KEE ---
TOKEN = '8798879670:AAGx_YvK1IlF21SQBmjtOmtEpDu7awheG00' 
bot = telebot.TeleBot(TOKEN)

# Kaardii Bingo qopheessuuf
def generate_bingo_card():
    card = []
    # Columns B, I, N, G, O (ranges 1-15, 16-30, etc.)
    ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
    for start, end in ranges:
        column = random.sample(range(start, end + 1), 5)
        card.append(column)
    
    # Gidduu kaardii sana 'FREE' gochuuf
    card[2][2] = "FREE"
    return card

def format_card(card):
    header = " B | I | N | G | O \n-------------------\n"
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
    
    bot.send_message(message.chat.id, "🎰 **Baga Gammaddan!**\nBingo Ethiopia-tti kaardii keessan fudhadhaa.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == '🎮 Tapha Jalqabi':
        card = generate_bingo_card()
        card_text = format_card(card)
        bot.send_message(message.chat.id, "🎲 Kunoo Kaardii keessan:\n\n" + card_text, parse_mode='MarkdownV2')
        bot.send_message(message.chat.id, "Lakkoofsota botiin waamu hordofaa!")
    elif message.text == '📜 Seera Taphaa':
        bot.reply_to(message, "📖 Seera: Kaardii kee irratti sarara tokko (line) yoo guutte kallaattiin 'BINGO' jedhi!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
