import os
import random
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. RENDER IRRATTI AKKA HIN CUFFAMNE (FLASK SETUP)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running!"

def run():
    # Render 'PORT' ofumaan siif kenna, yoo dhabame 10000 fayyadama
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. TELEGRAM BOT SETUP
# 'BOT_TOKEN' Render Environment Variables keessa galchuu hin dagatin
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Taphicha hordofuuf
game_state = {
    "is_active": False,
    "called_numbers": [],
    "user_selections": {} 
}

# 3. KEYBOARD 1-100 (FILANNOO)
def get_selection_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 101):
        buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"select_{i}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'new_game'])
def start_game(message):
    game_state["is_active"] = True
    game_state["called_numbers"] = []
    game_state["user_selections"][message.from_user.id] = []
    
    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Maaloo lakkofsa 1-100 gidduu jiran hanga 20 filadhu:",
        reply_markup=get_selection_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_selection(call):
    user_id = call.from_user.id
    selected_num = int(call.data.split('_')[1])
    
    if user_id not in game_state["user_selections"]:
        game_state["user_selections"][user_id] = []
        
    current = game_state["user_selections"][user_id]
    
    if selected_num in current:
        bot.answer_callback_query(call.id, "Lakkofsa kana duraan filatteetta!")
    elif len(current) >= 20:
        bot.answer_callback_query(call.id, "Lakkofsa 20 qofa filachuu dandeessa!")
    else:
        current.append(selected_num)
        bot.answer_callback_query(call.id, f"Lakkofsa {selected_num} filatteetta. ({len(current)}/20)")
        
        if len(current) == 20:
            bot.send_message(call.message.chat.id, "Lakkofsa 20 guuttatteetta! Taphni eegalamaa jira...")
            start_calling_numbers(call.message.chat.id)

# 4. WAAMICHA LAKKOFSAA FI INJIFANNOO
def start_calling_numbers(chat_id):
    if not game_state["is_active"]:
        return

    remaining = [n for n in range(1, 101) if n not in game_state["called_numbers"]]
    if not remaining:
        bot.send_message(chat_id, "Lakkofsi hundi waamameera!")
        return

    next_num = random.choice(remaining)
    game_state["called_numbers"].append(next_num)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("XUMURE! (Bingo)", callback_data="check_bingo"))
    
    bot.send_message(
        chat_id, 
        f"Lakkofsa Waamame: 🟢 {next_num}\nKuusaa: {game_state['called_numbers']}", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_bingo")
def check_bingo(call):
    user_id = call.from_user.id
    user_nums = game_state["user_selections"].get(user_id, [])
    called_nums = game_state["called_numbers"]
    
    is_winner = all(num in called_nums for num in user_nums)
    
    if is_winner:
        game_state["is_active"] = False # TAPHA DHAABUU
        bot.send_message(call.message.chat.id, f"🎉 🎉 BAGA GAMMADDAN! {call.from_user.first_name} injifateera. Taphni dhaabbateera.")
    else:
        bot.answer_callback_query(call.id, "Lakkofsi kee hundi hin waamamne. Itti fufi!", show_alert=True)
        start_calling_numbers(call.message.chat.id)

# 5. MAIN EXECUTION
if __name__ == "__main__":
    keep_alive() # Flask 'Web Server' jalqabsiisa
    print("Bot eegalamaa jira...")
    bot.infinity_polling()
