# 1. 'Variables' qarshii hordofan itti dabali
game_state = {
    "is_active": False,
    "called_numbers": [],
    "user_selections": {}, 
    "total_pool": 1000,    # Qarshii taphaaf madabame (Fakkeenyaaf)
    "user_balances": {}    # {user_id: balance}
}

# 2. Loojikii Injifannoo fi Hir'isummaa (30%)
@bot.callback_query_handler(func=lambda call: call.data == "check_bingo")
def check_bingo(call):
    user_id = call.from_user.id
    user_nums = game_state["user_selections"].get(user_id, [])
    called_nums = game_state["called_numbers"]
    
    is_winner = all(num in called_nums for num in user_nums)
    
    if is_winner:
        game_state["is_active"] = False
        
        # --- HERREGA QARSHII ---
        total_prize = game_state["total_pool"]
        tax_amount = total_prize * 0.30        # 30% hir'isuu
        final_win = total_prize - tax_amount   # Qarshii taphataaf hafu
        
        # Balance isaa irratti dabali
        game_state["user_balances"][user_id] = game_state["user_balances"].get(user_id, 0) + final_win
        
        # Beeksisa Injifannoo
        msg = (f"🎉 🎉 BAGA GAMMADDAN!\n\n"
               f"👤 Taphataa: {call.from_user.first_name}\n"
               f"🎟 Tikeetii: {user_nums}\n"
               f"💰 Gatii Madabame: {total_prize} ETB\n"
               f"📉 Komishinii (30%): {tax_amount} ETB\n"
               f"💵 Qarshii Mo'attan: {final_win} ETB\n\n"
               f"Qarshii keessan baafachuuf /withdraw fayyadamaa.")
        
        bot.send_message(call.message.chat.id, msg)
    else:
        bot.answer_callback_query(call.id, "Lakkofsi kee hundi hin waamamne!", show_alert=True)
        start_calling_numbers(call.message.chat.id)

# 3. Loojikii Qarshii Baafachuu (Withdraw)
@bot.message_handler(commands=['withdraw'])
def withdraw_money(message):
    user_id = message.from_user.id
    balance = game_state["user_balances"].get(user_id, 0)
    
    if balance > 0:
        bot.send_message(message.chat.id, f"💰 Balance keessan: {balance} ETB\nMaaloo lakkoofsa bilbilaa qarshiin irratti ergamu barreessaa.")
        # Asirratti loojikii kaffaltii (Manual ykn API) itti fufuu dandeessa
    else:
        bot.send_message(message.chat.id, "⚠️ Balance keessan 0 dha. Tapha mo'achuu qabdu.")
