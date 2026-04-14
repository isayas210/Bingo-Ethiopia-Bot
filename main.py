import telebot
from telebot import types
from flask import Flask, render_template_string, jsonify, request
from threading import Thread
import os
import random

app = Flask('')

# --- DATABASE SALPHAA ---
user_balances = {}

# --- BINGO LOGIC (B-I-N-G-O Prefix) ---
def get_bingo_label(num):
    if 1 <= num <= 15: return f"B-{num}"
    if 16 <= num <= 30: return f"I-{num}"
    if 31 <= num <= 45: return f"N-{num}"
    if 46 <= num <= 60: return f"G-{num}"
    if 61 <= num <= 75: return f"O-{num}"
    return str(num)

def generate_bingo_card():
    card = []
    ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
    for start, end in ranges:
        column = random.sample(range(start, end + 1), 5)
        card.append(column)
    card[2][2] = "FREE"
    return card

# --- API ---
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

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    uid = str(request.json.get('user_id'))
    current_bal = user_balances.get(uid, 0)
    if current_bal < 50:
        return jsonify({"error": "Baasuuf yoo xiqqaate 50 ETB qabaachuu qabdu!"}), 400
    user_balances[uid] = 0 # Simulation: Hunda baasuu
    return jsonify({"new_balance": 0, "msg": "Qarshiin keessan gara Telebirr-itti ergameera!"})

@app.route('/api/start_game', methods=['POST'])
def api_start():
    uid = str(request.json.get('user_id'))
    if user_balances.get(uid, 0) < 10:
        return jsonify({"error": "Balance gahaa miti!"}), 400
    user_balances[uid] -= 10
    card = generate_bingo_card()
    # Lakkoofsota waamaman prefix waliin qopheessuu
    raw_drawn = random.sample(range(1, 76), 15)
    labeled_drawn = [get_bingo_label(n) for n in raw_drawn]
    return jsonify({"card": card, "drawn": labeled_drawn, "new_balance": user_balances[uid]})

@app.route('/api/claim_win', methods=['POST'])
def api_win():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 0) + 50
    return jsonify({"new_balance": user_balances[uid]})

# --- FRONTEND (WITHDRAW & BINGO LABELS) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Bingo Ethiopia Super App</title>
    <style>
        body { background: #001489; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 10px; }
        .app-container { border: 2px solid #DBA111; border-radius: 20px; padding: 15px; background: rgba(0,0,0,0.9); min-height: 90vh; display: flex; flex-direction: column; }
        .balance-card { background: #000; border: 2px solid #00FF00; padding: 10px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 0 10px #00FF00; }
        .btn { padding: 12px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 8px; font-size: 1em; }
        .play-btn { background: #DBA111; color: black; font-size: 1.2em; }
        .dep-btn { background: #2ecc71; color: white; }
        .with-btn { background: #e74c3c; color: white; }
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 10px; }
        .cell { background: white; color: black; padding: 10px 2px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
        .cell.called { background: #00FF00; color: white; transform: scale(1.05); border: 1px solid white; }
        #draw-display { background: #DBA111; color: black; padding: 15px; border-radius: 10px; margin: 10px 0; font-weight: bold; font-size: 1.5em; border: 2px solid white; }
        .win-msg { color: #00FF00; font-weight: bold; font-size: 1.4em; }
    </style>
</head>
<body>
    <div class="app-container">
        <h2 style="color:#DBA111; margin-bottom:5px;">🎰 BINGO ETHIOPIA</h2>
        
        <div class="balance-card">
            <small style="color:#aaa;">HERREGA KEESSAN</small>
            <h3 id="bal-val" style="margin:5px 0; font-size:2em; color:#00FF00;">-- ETB</h3>
        </div>

        <div id="main-menu">
            <button class="btn play-btn" onclick="startGame()">🎮 TAPHA JALQABI (-10 ETB)</button>
            <button class="btn dep-btn" onclick="deposit()">💳 QARSHII GALCHI</button>
            <button class="btn with-btn" onclick="withdraw()">💰 QARSHII BAASI (WITHDRAW)</button>
        </div>

        <div id="game-section" style="display:none;">
            <div id="draw-display">Qophaa'aa...</div>
            <div id="win-area"></div>
            <div class="card-grid" id="bingo-card"></div>
        </div>
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

        async function withdraw() {
            const res = await fetch('/api/withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            if(data.error) { alert(data.error); }
            else { 
                alert(data.msg); 
                document.getElementById('bal-val').innerText = "0 ETB";
            }
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
                    document.getElementById('draw-display').innerText = "BINGO!";
                    document.getElementById('win-area').innerHTML = "<p class='win-msg'>🎉 INJIFATTEETTA! +50 ETB</p>";
                    const winRes = await fetch('/api/claim_win', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ user_id: uid })
                    });
                    const winData = await winRes.json();
                    document.getElementById('bal-val').innerText = winData.new_balance + " ETB";
                    setTimeout(() => { location.reload(); }, 4000);
                    return;
                }
                let label = data.drawn[i]; // Fkf: B-12
                let numOnly = label.split('-')[1]; // 12 qofa baasuu cell-f
                document.getElementById('draw-display').innerText = label;
                let cell = document.getElementById('c-'+numOnly);
                if(cell) cell.className = 'cell called';
                i++;
            }, 1500);
        }
        window.onload = loadData;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

TOKEN = '8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎰 BINGO LIVE BANAADHU", web_app=types.WebAppInfo(url="https://bingo-ethiopia-bot.onrender.com")))
    bot.send_message(message.chat.id, "👋 **Baga nagaan dhuftan!**\n\nBingo Ethiopia haala haaraan qophaa'ee dhufeera. Hojiin hundi (Deposit, Withdraw, Game) App keessatti raawwatama.", reply_markup=markup, parse_mode='Markdown')

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    bot.infinity_polling()
