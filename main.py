import os
import random
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. RENDER SERVER (Port akka hin cufamne)
app = Flask('')
@app.route('/')
def home(): return "Bingo Ethiopia is Live!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 2. BOT SETUP
API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = "YOUR_TELEGRAM_ID_HERE"  # ID kee isa 'userinfobot' irraa fuute as galchi
bot = telebot.TeleBot(API_TOKEN)

# DATA STORAGE
game_state = {
    "is_active": False,
    "called_numbers": [],
    "user_selections": {},
    "user_balances": {}, # {user_id: balance}
    "total_pool": 0      # Qarshii tapha tokkoof madabame
}

# 3. DEPOSIT (CBE & CBE BIRR)
@bot.message_handler(commands=['deposit'])
def deposit(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("CBE Bank", callback_data="pay_cbe"))
    markup.add(types.InlineKeyboardButton("CBE Birr", callback_data="pay_cbe_birr"))
    
    bot.send_message(message.chat.id, "Maaloo karaa kaffaltii filadhaa:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment_method(call):
    method = "CBE Bank (1000xxxx)" if call.data == "pay_cbe" else "CBE Birr (09xxxxxxxx)"
    msg = (f"💰 **Kaffaltii Raawwadhaa**\n\nLakk: {method}\n"
           "Erga kaffaltanii booda 'Screenshot' ykn Lakk. Transaction natti ergaa.\n"
           "Admin erga mirkaneessee booda Balance keessan ni haaroma.")
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

# 4. INJIFANNOO FI HIR'ISUMMAA 30%
@bot.callback_query_handler(func=lambda call: call.data == "check_bingo")
def check_bingo(call):
    user_id = call.from_user.id
    user_nums = game_state["user_selections"].get(user_id, [])
    called_nums = game_state["called_numbers"]
    
    if all(num in called_nums for num in user_nums):
        game_state["is_active"] = False
        
        # HERREGA QARSHII
        pool = game_state["total_pool"]
        tax = pool * 0.30          # 30% Hir'isuu (Komishinii)
        final_win = pool - tax     # 70% Taphataaf
        
        game_state["user_balances"][user_id] = game_state["user_balances"].get(user_id, 0) + final_win
        
        result_msg = (f"🎉 **BAGA GAMMADDAN!**\n\n"
                      f"👤 Taphataa: {call.from_user.first_name}\n"
                      f"💰 Pool Guutuu: {pool} ETB\n"
                      f"📉 Komishinii (30%): {tax} ETB\n"
                      f"💵 Qarshii Mo'attan: {final_win} ETB\n"
                      "Qarshii keessan baafachuuf /withdraw fayyadamaa.")
        bot.send_message(call.message.chat.id, result_msg, parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "Lakkofsi kee hundi hin waamamne!", show_alert=True)

# 5. WITHDRAW (CBE & CBE BIRR)
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    balance = game_state["user_balances"].get(message.from_user.id, 0)
    if balance < 50:
        bot.send_message(message.chat.id, f"⚠️ Balance keessan {balance} ETB qofa. Baafachuuf yoo xiqqaate 50 ETB barbaachisa.")
        return
    
    msg = bot.send_message(message.chat.id, "Maaloo Lakk. Bilbilaa (CBE Birr) ykn Lakk. Herregaa (CBE) galchaa:")
    bot.register_next_step_handler(msg, process_withdraw, balance)

def process_withdraw(message, balance):
    account_info = message.text
    # Gara Adminitti ergaa
    bot.send_message(ADMIN_ID, f"🔔 **GAAFFII WITHDRAW**\n\nNamni: {message.from_user.first_name}\nLakk: {account_info}\nHanga: {balance} ETB")
    bot.send_message(message.chat.id, "✅ Gaaffiin keessan Adminitti ergameera. Sa'aatii muraasa keessatti isiniif deebi'a.")

# MAIN LOOP
if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.infinity_polling()
