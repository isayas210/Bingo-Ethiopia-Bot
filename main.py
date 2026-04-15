import telebot
from flask import Flask
import os
from threading import Thread
import time
import json
import requests

# CONFIG
BOT_TOKEN = "8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c"
ADMIN_ID = 6365691079 
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# DATABASE
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- TELEGRAM BOT LOGIC ---

@bot.message_handler(commands=['start'])
def start(message):
    db = load_db()
    uid = str(message.from_user.id)
    if uid not in db:
        db[uid] = {"balance": 0.0, "name": message.from_user.first_name}
        save_db(db)
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎮 Tapha Jalqabi", "💰 Deposit", "💸 Withdraw", "📊 Herrega Koo")
    
    bot.send_message(message.chat.id, 
        f"<b>Baga nagaan dhufte, {message.from_user.first_name}!</b>\n💰 Herrega kee: <b>{db[uid]['balance']:.2f} ETB</b>", 
        parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 Deposit")
def deposit(message):
    msg = (
        "<b>🏦 Akkaataa Kaffaltii:</b>\n"
        "📱 Telebirr: <code>0974085753</code>\n"
        "🏦 CBE Bank: <code>1000659750973</code>\n\n"
        "⚠️ Erga kaffaltii raawwattanii booda, <b>Screenshot</b> nuuf ergaa."
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "💸 Withdraw")
def withdraw(message):
    bot.send_message(message.chat.id, "<b>💸 Withdraw:</b>\nHamma baasuu barbaaddanii fi Lakk. bilbilaa galchaa.\nFkn: 500 ETB, 09xxxxxxxx", parse_mode="HTML")

@bot.message_handler(content_types=['photo', 'text'])
def handle_requests(message):
    uid = str(message.from_user.id)
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"🔔 <b>DEPOSIT!</b> ID: <code>{uid}</code>", parse_mode="HTML")
        bot.send_message(message.chat.id, "✅ Screenshot keessan nu ga'eera.")
    elif uid != str(ADMIN_ID) and message.text and any(x in message.text.lower() for x in ["etb", "birr", "baasu"]):
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ Gaaffiin keessan Admin bira ga'eera.")

@bot.message_handler(commands=['add'])
def add_money(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # /add 12345 500 (Akka kanaan fayyadami)
            parts = message.text.split()
            tid = parts[1]
            amt = parts[2]
            db = load_db()
            if tid in db:
                db[tid]["balance"] += float(amt)
                save_db(db)
                bot.send_message(tid, f"🎉 Herregni kee <b>{amt} ETB</b> dabalameera!", parse_mode="HTML")
                bot.send_message(ADMIN_ID, f"✅ User {tid} irratti {amt} dabalameera.")
        except: bot.send_message(ADMIN_ID, "Format: /add USERID AMOUNT")

# --- WEB UI ---
@app.route('/')
def home():
    return "<h1>Bingo Ethiopia Live is Running</h1>"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    # Force clear sessions (Fix Conflict 409)
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True")
    except:
        pass
        
    time.sleep(5)
    
    # START POLLING (Faulty keyword removed)
    print("Bot is starting...")
    bot.infinity_polling(timeout=20)
