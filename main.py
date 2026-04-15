import telebot
from flask import Flask
import os
from threading import Thread
import time
import json
import requests

# CONFIG
BOT_TOKEN = "8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c"
# Admin ID kee (Asitti ID kee isa dhugaa bakka buusi)
ADMIN_ID = 6365691079 
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# DATABASE (Fayyadamtoota kuusuuf)
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

# MENU JALQABAA (MAIN MENU)
@bot.message_handler(commands=['start'])
def start(message):
    db = load_db()
    uid = str(message.from_user.id)
    if uid not in db:
        db[uid] = {"balance": 0.0, "name": message.from_user.first_name}
        save_db(db)
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = telebot.types.KeyboardButton("🎮 Tapha Jalqabi")
    btn2 = telebot.types.KeyboardButton("💰 Deposit")
    btn3 = telebot.types.KeyboardButton("💸 Withdraw")
    btn4 = telebot.types.KeyboardButton("📊 Herrega Koo")
    markup.add(btn1, btn2, btn3, btn4)
    
    welcome_text = (
        f"<b>Baga nagaan dhufte, {message.from_user.first_name}!</b> 🇪🇹\n\n"
        f"💰 Herrega kee: <b>{db[uid]['balance']:.2f} ETB</b>\n\n"
        "Tapha jalqabuuf button gadii tuqi."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

# HERREGA KOO
@bot.message_handler(func=lambda m: m.text == "📊 Herrega Koo")
def check_balance(message):
    db = load_db()
    uid = str(message.from_user.id)
    bal = db.get(uid, {}).get("balance", 0)
    bot.send_message(message.chat.id, f"💰 Herrega kee: <b>{bal:.2f} ETB</b>", parse_mode="HTML")

# DEPOSIT HANDLER
@bot.message_handler(func=lambda m: m.text == "💰 Deposit")
def deposit(message):
    msg = (
        "<b>🏦 Akkaataa Kaffaltii:</b>\n"
        "--------------------------\n"
        "📱 <b>Telebirr:</b> <code>0974085753</code>\n"
        "🏦 <b>CBE Bank:</b> <code>1000659750973</code>\n"
        "--------------------------\n"
        "⚠️ <b>Hubachiisa:</b> Erga kaffaltii raawwattanii booda, <b>Screenshot</b> nuuf ergaa. "
        "Nutis herrega keessan ni dabalra."
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# WITHDRAW HANDLER
@bot.message_handler(func=lambda m: m.text == "💸 Withdraw")
def withdraw(message):
    msg = (
        "<b>💸 Maallaqa Baasuu:</b>\n\n"
        "Hamma baasuu barbaaddanii fi Lakk. herrega keessanii nuuf barreessaa.\n"
        "<i>Fkn: 500 ETB, Telebirr 09xxxxxxxx</i>"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# SCREENSHOT & REQUESTS HANDLING
@bot.message_handler(content_types=['photo', 'text'])
def handle_requests(message):
    uid = str(message.from_user.id)
    # Screenshot yoo ta'e
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"🔔 <b>DEPOSIT REQUEST!</b>\nUser: {message.from_user.first_name}\nID: <code>{uid}</code>", parse_mode="HTML")
        bot.send_message(message.chat.id, "✅ Screenshot keessan nu ga'eera. Mirkaneessinee herrega keessan ni dabalra.")
    
    # Withdraw request yoo ta'e (text)
    elif "Withdraw" not in message.text and uid != str(ADMIN_ID):
        if any(x in message.text.lower() for x in ["etb", "baasu", "birr"]):
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(ADMIN_ID, f"⚠️ <b>WITHDRAW REQUEST!</b>\nUser: {message.from_user.first_name}\nID: <code>{uid}</code>", parse_mode="HTML")
            bot.send_message(message.chat.id, "✅ Gaaffiin keessan Admin bira ga'eera. Kaffaltiin isiniif ni raawwatama.")

# ADMIN: ADD BALANCE (Fkn: /add_12345_500)
@bot.message_handler(commands=['add'])
def add_balance_cmd(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, target_id, amount = message.text.split("_")
            db = load_db()
            if target_id in db:
                db[target_id]["balance"] += float(amount)
                save_db(db)
                bot.send_message(ADMIN_ID, f"✅ User {target_id} irratti {amount} ETB dabalameera.")
                bot.send_message(target_id, f"🎉 <b>Herregni kee dabalameera!</b>\n+{amount} ETB dabalame. Amma taphachuu dandeessa.", parse_mode="HTML")
        except:
            bot.send_message(ADMIN_ID, "Dogoggora! Akkasitti fayyadami: /add_USERID_AMOUNT")

# MINI APP HTML (V24 Stable)
@app.route('/')
def home():
    return """
    <h1 style='color:white; text-align:center;'>Bingo Ethiopia Live UI</h1>
    """

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Force clear sessions
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True")
    time.sleep(20)
    
    print("Bot is running...")
    bot.infinity_polling(skip_pending_updates=True)
