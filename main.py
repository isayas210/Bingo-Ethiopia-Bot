import telebot
from telebot import types
from flask import Flask, render_template_string, jsonify, request
from threading import Thread
import os
import random
import time

app = Flask('')

# --- DATABASE SALPHAA ---
user_balances = {}

# --- BINGO LOGIC ---
def generate_bingo_card():
    card = []
    ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
    for start, end in ranges:
        column = random.sample(range(start, end + 1), 5)
        card.append(column)
    card[2][2] = "FREE"
    return card

# --- API FOR MINI APP ---
@app.route('/api/start_game', methods=['POST'])
def api_start():
    data = request.json
    uid = data.get('user_id')
    if user_balances.get(uid, 0) < 10:
        return jsonify({"error": "Balance keessan gahaa miti!"}), 400
    
    user_balances[uid] -= 10
    card = generate_bingo_card()
    drawn_numbers = random.sample(range(1, 76), 15) # Lakkoofsota 15 waamaman
    return jsonify({
        "card": card,
        "drawn": drawn_numbers,
        "new_balance": user_balances[uid]
    })

# --- FRONTEND (ALL-IN-ONE DESIGN) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Bingo Ethiopia Live</title>
    <style>
        body { background: #001489; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
        .container { border: 2px solid #DBA111; border-radius: 15px; padding: 15px; background: rgba(0,0,0,0.8); }
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 15px; }
        .cell { background: white; color: black; padding: 10px 5px; border-radius: 5px; font-weight: bold; font-size: 0.9em; }
        .cell.called { background: #00FF00; }
        .draw-box { background: #DBA111; color: black; padding: 10px; margin: 15px 0; border-radius: 10px; font-weight: bold; }
        .play-btn { background: #DBA111; color: black; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; }
        #balance-display { color: #00FF00; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎰 BINGO LIVE</h2>
        <div id="balance-display">💰 Balance: 10 ETB</div>
        
        <div id="game-area" style="display:none;">
            <div class="draw-box" id="current-number">Lakkoofsa Eeggachaa...</div>
            <div class="card-grid" id="bingo-card"></div>
        </div>

        <button class="play-btn" id="main-btn" onclick="startGame()">TAPHA JALQABI (-10 ETB)</button>
        <p id="status"></p>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();

        async function startGame() {
            const btn = document.getElementById('main-btn');
            btn.disabled = true;
            document.getElementById('status').innerText = "Taphichi jalqabaa jira...";

            try {
                // Kallaattiin koodii Python (API) waliin dubbachuuf
                const response = await fetch('/api/start_game', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: tg.initDataUnsafe.user.id })
                });
                
                const data = await response.json();
                if(data.error) {
                    alert(data.error);
                    btn.disabled = false;
                    return;
                }

                document.getElementById('balance-display').innerText = "💰 Balance: " + data.new_balance + " ETB";
                document.getElementById('game-area').style.display = "block";
                renderCard(data.card);
                startDrawing(data.drawn);
                
            } catch (e) {
                console.error(e);
            }
        }

        function renderCard(card) {
            const grid = document.getElementById('bingo-card');
            grid.innerHTML = "";
            for(let i=0; i<5; i++) {
                for(let j=0; j<5; j++) {
                    const div = document.createElement('div');
                    div.className = "cell";
                    div.innerText = card[j][i];
                    div.id = "cell-" + card[j][i];
                    grid.appendChild(div);
                }
            }
        }

        function startDrawing(numbers) {
            let i = 0;
            const interval = setInterval(() => {
                if(i >= numbers.length) {
                    clearInterval(interval);
                    document.getElementById('current-number').innerText = "Tapha Xumure!";
                    return;
                }
                const num = numbers[i];
                document.getElementById('current-number').innerText = "Lakkoofsa: " + num;
                const cell = document.getElementById("cell-" + num);
                if(cell) cell.className = "cell called";
                i++;
            }, 2000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c' 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 10
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🎰 Open Bingo Live", web_app=types.WebAppInfo(url="https://bingo-ethiopia-bot.onrender.com"))
    markup.add(btn)
    bot.send_message(message.chat.id, "Baga nagaatti dhuftan! Tapha Bingo dhugaa kallaattiin App keessaatti taphachuuf kan gadii xuqaa.", reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
