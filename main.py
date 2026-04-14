import os
import random
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. SERVER SETUP (Render Port Fix)
app = Flask('')
@app.route('/')
def home(): return "Bingo Ethiopia Bot is Active!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 2. BOT CONFIGURATION
API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 123456789  # ID kee asitti jijjiiri (Fkn: 56789123)
bot = telebot.TeleBot(API_TOKEN)

# DATABASE
game_data = {
    "is_active": False,
    "called_numbers": [],
    "user_selections": {}, 
    "balances": {},        
    "total_pool": 0        
}

# 3. DEPOSIT SECTION (Admin Approval)
@bot.message_handler(commands=['deposit'])
def deposit_options(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("CBE Bank 🏦", callback_data="pay_cbe"),
        types.InlineKeyboardButton("CBE Birr 📱", callback_data="pay_cbebirr")
    )
    bot.send_message(message.chat.id, "💰 **Kaffaltii Raawwachuuf Filadhaa:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment(call):
    method = "CBE Bank (1000xxxx)" if call.data == "pay_cbe" else "CBE Birr (09xxxxxxxx)"
    msg = (f"💳 **{method}**\n\nMaaloo kaffaltii erga raawwattanii booda **Screenshot** ragaa kaffaltii natti ergaa.\n\n"
           "Admin erga mirkaneessee booda Balance keessan ni haaroma.")
    bot.send_message(call.message.chat.id, msg)
    bot.register_next_step_handler(call.message, forward_to_admin)

def forward_to_admin(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Mirkaneessi ✅", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("Kufisi ❌", callback_data=f"decline_{user_id}")
    )
    
    bot.send_message(ADMIN_ID, f"🔔 **GAAFFII DEPOSIT**\nUser: {user_name}\nID: {user_id}", reply_markup=markup)
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Ragaan keessan Adminitti ergameera. Xiqqoo eegaa.")

# 4. WIN LOGIC (30% Commission)
@bot.callback_query_handler(func=lambda call: call.data == "check_bingo")
def check_winner(call):
    user_id = call.from_user.id
    user_nums = game_data["user_selections"].get(user_id, [])
    called = game_data["called_numbers"]
    
    if all(n in called for n in user_nums):
        game_data["is_active"] = False
        pool = game_data["total_pool"]
        tax = pool * 0.30  # 30% Profit
        final_win = pool - tax
        
        game_data["balances"][user_id] = game_data["balances"].get(user_id, 0) + final_win
        
        msg = (f"🎉 **🎉 BAGA GAMMADDAN!**\n\n"
               f"💰 Pool: {pool} ETB\n"
               f"📉 Komishinii (30%): {tax} ETB\n"
               f"💵 Qarshii Mo'attan: **{final_win} ETB**\n\n"
               "Baafachuuf /withdraw fayyadamaa.")
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "Lakkofsi kee hundi hin waamamne!", show_alert=True)

# 5. WITHDRAW SECTION (CBE & CBE Birr)
@bot.message_handler(commands=['withdraw'])
def withdraw_start(message):
    balance = game_data["balances"].get(message.from_user.id, 0)
    if balance < 50:
        bot.send_message(message.chat.id, "⚠️ Balance keessan gadi aanaadha (Min: 50 ETB).")
        return
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("CBE Bank", "CBE Birr")
    msg = bot.send_message(message.chat.id, "Maaloo bakka qarshiin itti ergamu filadhaa:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_withdraw_details, balance)

def process_withdraw_details(message, amount):
    method = message.text
    msg = bot.send_message(message.chat.id, f"Maaloo Lakk. {method} keessan galchaa:")
    bot.register_next_step_handler(msg, send_withdraw_to_admin, amount, method)

def send_withdraw_to_admin(message, amount, method):
    account = message.text
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Kaffalameera ✅", callback_data=f"paid_{user_id}_{amount}"))
    
    bot.send_message(ADMIN_ID, f"💸 **GAAFFII WITHDRAW**\nUser: {message.from_user.first_name}\nMethod: {method}\nLakk: {account}\nHanga: {amount} ETB", reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Gaaffiin keessan Adminitti ergameera. Kaffaltiin yeroo raawwatamu beeksisa ni argattu.")

# 6. ADMIN ACTIONS (Approve/Paid)
@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    data = call.data.split('_')
    
    if data[0] == "approve":
        u_id = int(data[1])
        bot.send_message(u_id, "✅ Kaffaltiin keessan mirkanaa'eera! Balance keessan haaromeera.")
        bot.edit_message_text("✅ Deposit Mirkanaa'eera.", call.message.chat.id, call.message.message_id)
        
    elif data[0] == "paid":
        u_id, amt = int(data[1]), float(data[2])
        game_data["balances"][u_id] = game_data["balances"].get(u_id, 0) - amt
        bot.send_message(u_id, f"✅ Qarshiin keessan {amt} ETB isiniif ergameera. Galatoomaa!")
        bot.edit_message_text(f"✅ Kaffaltiin {amt} ETB xumurameera.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
