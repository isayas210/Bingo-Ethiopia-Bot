import telebot
from telebot import types
from flask import Flask, render_template_string, jsonify, request
from threading import Thread
import os
import random

app = Flask('')

# --- DATABASE SALPHAA (RAM irratti) ---
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
@app.route('/api/get_user_data', methods=['POST'])
def get_data():
    uid = str(request.json.get('user_id'))
    if uid not in user_balances: user_balances[uid] = 10
    return jsonify({"balance": user_balances[uid]})

@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 10) + 50
    return jsonify({"new_balance": user_balances[uid]})

@app.route('/api/start_game', methods=['POST'])
def api_start():
    uid = str(request.json.get('user_id'))
    if user_balances.get(uid, 0) < 10:
        return jsonify({"error": "Qarshiin gahaa miti!"}), 400
    
    user_balances[uid] -= 10
    card = generate_bingo_card()
    drawn_numbers = random.sample(range(1, 76), 15) 
    return jsonify({
        "card": card, 
        "drawn": drawn_numbers, 
        "new_balance": user_balances[uid]
    })

@app.route('/api/claim_win', methods=['POST'])
def api_win():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 0) + 50
    return jsonify({"new_balance": user_balances[uid]})

# --- FRONTEND (ALL-IN-APP DESIGN) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Bingo Ethiopia Super App</title>
    <style>
        body { background: #001489; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
        .app-container { border: 2px solid #DBA111; border-radius: 20px; padding: 15px; background: rgba(0,0,0,0.9); min-height: 90vh; display: flex; flex-direction: column; }
        .balance-card { background: #111; border: 2px solid #00FF00; padding: 10px; border-radius: 12px; margin-bottom: 15px; }
        .balance-card h3 { margin: 5px 0; color: #00FF00; font-size: 1.8em; }
        .btn { padding: 12px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 10px; }
        .play-btn { background: #DBA111; color: black; font-size: 1.2em; }
        .dep-btn { background: #2ecc71; color: white; }
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 10px; }
        .cell { background: white; color: black; padding: 10px 2px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
        .cell.called { background: #00FF00; color: white; transform: scale(1.1); }
        #draw-display { background: #DBA111; color: black; padding: 12px; border-radius: 10px; margin: 10px 0; font-weight: bold; font-size: 1.3em; }
        .win-msg { color: #00FF00; font-weight: bold; font-size: 1.5em; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="app-container">
        <h2 style="color:#DBA111;">🎰 BINGO ETHIOPIA</h2>
        
        <div class="balance-card">
            <small>Balance Keessan</small>
            <h3 id="bal-val">-- ETB</h3>
        </div>

        <div id="main-menu">
            <button class="btn dep-btn" onclick="deposit()">💳 QARSHII GALCHI (DEPOSIT)</button>
            <button class="btn play-btn" onclick="startGame()">🎮 TAPHA JALQABI (-10 ETB)</button>
        </div>

        <div id="game-section" style="display:none;">
            <div id="draw-display">Lakkoofsa Eeggachaa...</div>
            <div id="win-area"></div>
            <div class="card-grid" id="bingo-card"></div>
        </div>

        <div style="margin-top:auto; font-size:0.7em; color:#666;">Bingo Ethiopia Official Bot</div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let uid = tg.initDataUnsafe.user.id;

        async function loadData() {
            const res = await fetch('/api/get_user_data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.balance + " ETB";
        }

        async function deposit() {
            const res = await fetch('/api/deposit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
        }

        async function startGame() {
            document.getElementById('main-menu').style.display = "none";
            const res = await fetch('/api/start_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            if(data.error) { alert(data.error); document.getElementById('main-menu').style.display = "block"; return; }

            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
            document.getElementById('game-section').style.display = "block";
            
            const grid = document.getElementById('bingo-card');
            grid.innerHTML = "";
            data.card.forEach(col => col.forEach(val => {
                let d = document.createElement('div');
                d.className = 'cell'; d.innerText = val; d.id = 'c-'+val;
                grid.appendChild(d);
            }));

            let i = 0;
            let timer = setInterval(async () => {
                if(i >= data.drawn.length) {
                    clearInterval(timer);
                    document.getElementById('draw-display').innerText = "TAPHA XUMURE!";
                    document.getElementById('win-area').innerHTML = "<p class='win-msg'>🎉 INJIFATTEETTA! +50 ETB</p>";
                    // Kallaattiin badhaasa kaffaluu
                    const winRes = await fetch('/api/claim_win', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ user_id: uid })
                    });
                    const winData = await winRes.json();
                    document.getElementById('bal-val').innerText = winData.new_balance + " ETB";
                    
                    setTimeout(() => { location.reload(); }, 5000);
                    return;
                }
                let n = data.drawn[i];
                document.getElementById('draw-display').innerText = "LAKKOOFSA: " + n;
                let cell = document.getElementById('c-'+n);
                if(cell) cell.className = 'cell called';
                i++;
            }, 1000);
        }

        window.onload = loadData;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- TOKEN ---
TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    # Button maqaan isaa qofaan miidhage
    markup.add(types.InlineKeyboardButton("🎰 BINGO BANAADHU", web_app=types.WebAppInfo(url="https://bingo-ethiopia-bot.onrender.com")))
    bot.send_message(message.chat.id, "👋 **Baga nagaan dhuftan!**\n\nTapha Bingo kallaattiin taphachuuf kan gadii xuqaa. Hojiin hundi App keessatti raawwatama.", reply_markup=markup, parse_mode='Markdown')

# Botiin ergaa biraa akka hin ergineef 'handle_app_data' haqameera.

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
