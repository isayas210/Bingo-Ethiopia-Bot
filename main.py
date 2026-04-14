import telebot
from telebot import types
import random

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

# Haala taphaa hordofuuf (Database iddoo bu'a)
game_state = {
    "is_active": False,
    "called_numbers": [],
    "winners": [],
    "user_selections": {}  # {user_id: [list_of_numbers]}
}

# 1. Keyboard lakkofsa 1-100 filachiisu (Hanga 20)
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
    game_state["winners"] = []
    game_state["user_selections"][message.from_user.id] = []
    
    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Maaloo lakkofsa 1-100 gidduu jiran hanga 20 filadhu:",
        reply_markup=get_selection_keyboard()
    )

# 2. Lakkofsa filataman hordofuu
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_selection(call):
    user_id = call.from_user.id
    selected_num = int(call.data.split('_')[1])
    
    if user_id not in game_state["user_selections"]:
        game_state["user_selections"][user_id] = []
        
    current_selections = game_state["user_selections"][user_id]
    
    if selected_num in current_selections:
        bot.answer_callback_query(call.id, "Lakkofsa kana duraan filatteetta!")
    elif len(current_selections) >= 20:
        bot.answer_callback_query(call.id, "Lakkofsa 20 qofa filachuu dandeessa!")
    else:
        current_selections.append(selected_num)
        bot.answer_callback_query(call.id, f"Lakkofsa {selected_num} filatteetta. ({len(current_selections)}/20)")
        
        # Yoo 20 guute tapha eegalchiisuu dandeessa
        if len(current_selections) == 20:
            bot.send_message(call.message.chat.id, "Lakkofsa 20 guuttateetta! Taphni eegalamaa jira...")
            start_calling_numbers(call.message.chat.id)

# 3. Lakkofsa waamuu fi Injifannoo Check gochuu
def start_calling_numbers(chat_id):
    if not game_state["is_active"]:
        return

    # Lakkofsa hin waamamin keessaa tokko fili
    remaining = [n for n in range(1, 101) if n not in game_state["called_numbers"]]
    if not remaining:
        bot.send_message(chat_id, "Lakkofsi hundi waamameera!")
        return

    next_num = random.choice(remaining)
    game_state["called_numbers"].append(next_num)
    
    # Ergaa lakkofsa waamamee ergi
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("XUMURE! (Bingo)", callback_data="check_bingo"))
    
    bot.send_message(
        chat_id, 
        f"Lakkofsa Waamame: 🟢 {next_num}\nKuusaa: {game_state['called_numbers']}", 
        reply_markup=markup
    )

# 4. Yeroo 'Xumure' jedhamu dhaabuu
@bot.callback_query_handler(func=lambda call: call.data == "check_bingo")
def check_bingo(call):
    user_id = call.from_user.id
    user_nums = game_state["user_selections"].get(user_id, [])
    called_nums = game_state["called_numbers"]
    
    # Check: Lakkofsi taphataa hundi waamameera?
    is_winner = all(num in called_nums for num in user_nums)
    
    if is_winner:
        game_state["is_active"] = False  # TAPHA DHAABUU
        bot.send_message(call.message.chat.id, f"🎉 BAGA GAMMADDAN! Taphataan {call.from_user.first_name} injifateera. Taphni dhaabbateera.")
        bot.send_message(call.message.chat.id, "Tapha haaraa eegaluuf /new_game fayyadamaa.")
    else:
        bot.answer_callback_query(call.id, "Lakkofsi kee hundi hin waamamnne. Itti fufi!", show_alert=True)
        # Taphni itti fufa
        start_calling_numbers(call.message.chat.id)

if __name__ == "__main__":
    print("Bot eegaleera...")
    bot.polling()
