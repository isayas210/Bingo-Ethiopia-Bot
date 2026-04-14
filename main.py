import telebot
from telebot import types
from flask import Flask, render_template_string, jsonify, request
from threading import Thread
import os
import random

app = Flask('')

# --- DATABASE SALPHAA ---
user_balances = {}

# --- BINGO LOGIC ---
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

@app.route('/api/confirm_deposit', methods=['POST'])
def confirm_deposit():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 10) + 50
    return jsonify({"new_balance": user_balances[uid]})

@app.route('/api/start_game', methods=['POST'])
def api_start():
    uid = str(request.json.get('user_id'))
    if user_balances.get(uid, 0) < 10:
        return jsonify({"error": "Balance gahaa miti!"}), 400
    user_balances[uid] -= 10
    card = generate_bingo_card()
    raw_drawn = random.sample(range(1, 76), 20) # Lakkoofsa 20 waamuuf
    labeled_drawn = [get_bingo_label(n) for n in raw_drawn]
    return jsonify({"card": card, "drawn": labeled_drawn, "new_balance": user_balances[uid]})

# --- FRONTEND ---
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
        .app-container { border: 2px solid #DBA111; border-radius: 20px; padding: 15px; background: rgba(0,0,0,0.95); min-height: 90vh; }
        .balance-card { background: #000; border: 2px solid #00FF00; padding: 10px; border-radius: 12px; margin-bottom: 15px; }
        .btn { padding: 12px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 8px; }
        .play-btn { background: #DBA111; color: black; }
        .info-panel { background: #222; padding: 15px; border-radius: 10px; text-align: left; font-size: 0.85em; display: none; margin-bottom: 10px; border: 1px solid #DBA111; }
        
        /* Ticket Selection */
        .ticket-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; max-height: 200px; overflow-y: auto; background: #111; padding: 10px; border-radius: 10px; }
        .t-btn { background: #444; color: white; border: 1px solid #DBA111; padding: 8px; border-radius: 5px; cursor: pointer; }
        .t-btn.selected { background: #DBA111; color: black; }

        /* Game UI */
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 10px; }
        .cell { background: white; color: black; padding: 10px 2px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
        .cell.called { background: #00FF00; color: white; }
        .history-box { background: #111; padding: 10px; border-radius: 10px; margin-top: 10px; font-size: 0.8em; color: #00FF00; text-align: left; min-height: 40px; border: 1px solid #444; }
        
        /* Upload Section */
        .upload-box { margin-top: 10px; border-top: 1px solid #444; padding-top: 10px; }
        input[type="file"] { font-size: 0.8em; color: #DBA111; }
    </style>
</head>
<body>
    <div class="app-container">
        <h2 style="color:#DBA111;">🎰 BINGO ETHIOPIA</h2>

        <div class="balance-card">
            <small>BALANCE</small>
            <h3 id="bal-val" style="color:#00FF00; font-size:2em; margin:5px 0;">-- ETB</h3>
        </div>

        <div id="ticket-stage">
            <p>Maaloo Tikeetii Filadhaa (1-100)</p>
            <div class="ticket-grid" id="t-grid"></div>
            <p id="sel-info" style="color:#DBA111; font-weight:bold;"></p>
            <button class="btn play-btn" id="start-btn" onclick="startGame()" style="display:none;">🎮 TAPHA JALQABI</button>
        </div>

        <div id="game-section" style="display:none;">
            <div id="draw-display" style="background:#DBA111; color:black; padding:15px; border-radius:10px; font-weight:bold; font-size:1.5em;">...</div>
            <div class="history-box" id="history">Kuusaa: </div>
            <div class="card-grid" id="bingo-card"></div>
        </div>

        <div id="footer-menu" style="margin-top:15px;">
            <button class="btn" style="background:#2ecc71; color:white;" onclick="toggleDeposit()">💳 DEPOSIT</button>
            <div id="deposit-info" class="info-panel">
                📱 Telebirr/CBE Birr: 0974085753<br>
                🏦 CBE: 1000659750973<br>
                👤 Isayas Emana<br><br>
                <div class="upload-box">
                    <small>Screenshot Upload:</small><br>
                    <input type="file" id="ss-file" accept="image/*"><br><br>
                    <button class="btn" style="background:#00FF00; color:black; padding:5px;" onclick="confirmDep()">✅ MIRKANEESSI</button>
                </div>
            </div>
            <button class="btn" style="background:#e74c3c; color:white;" onclick="requestWithdraw()">💰 WITHDRAW</button>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let uid = tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : "123";
        let selectedTicket = null;

        // Tikeetii 100 uumuu
        const tGrid = document.getElementById('t-grid');
        for(let i=1; i<=100; i++) {
            let b = document.createElement('button');
            b.innerText = i;
            b.className = 't-btn';
            b.onclick = () => {
                selectedTicket = i;
                document.querySelectorAll('.t-btn').forEach(x => x.classList.remove('selected'));
                b.classList.add('selected');
                document.getElementById('sel-info').innerText = "Tikeetii #" + i + " filatteetta!";
                document.getElementById('start-btn').style.display = 'block';
            };
            tGrid.appendChild(b);
        }

        async function loadData() {
            const res = await fetch('/api/get_user_data', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.balance + " ETB";
        }

        function toggleDeposit() {
            let panel = document.getElementById('deposit-info');
            panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
        }

        async function confirmDep() {
            const fileInput = document.getElementById('ss-file');
            if(!fileInput.files[0]) { alert("Maaloo dura Screenshot upload godhaa!"); return; }
            
            const res = await fetch('/api/confirm_deposit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
            alert("Mirkanaa'eera! Balance keessan ni dabalame.");
        }

        async function startGame() {
            document.getElementById('ticket-stage').style.display = "none";
            document.getElementById('footer-menu').style.display = "none";
            const res = await fetch('/api/start_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            if(data.error) { alert(data.error); location.reload(); return; }

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
            let historyArr = [];
            let timer = setInterval(() => {
                if(i >= data.drawn.length) {
                    clearInterval(timer);
                    document.getElementById('draw-display').innerText = "XUMURE!";
                    setTimeout(() => { location.reload(); }, 5000);
                    return;
                }
                let label = data.drawn[i];
                let numOnly = label.split('-')[1];
                document.getElementById('draw-display').innerText = label;
                
                // History kuusuu
                historyArr.push(label);
                document.getElementById('history').innerText = "Kuusaa: " + historyArr.join(", ");
                
                let cell = document.getElementById('c-'+numOnly);
                if(cell) cell.className = 'cell called';
                i++;
            }, 1500);
        }

        function requestWithdraw() {
            let bal = parseInt(document.getElementById('bal-val').innerText);
            if(bal < 50) alert("Balance gahaa miti!");
            else { tg.sendData("WITHDRAW_REQUEST_" + bal); tg.close(); }
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
    markup.add(types.InlineKeyboardButton("🎰 BINGO BANAADHU", web_app=types.WebAppInfo(url="https://bingo-ethiopia-bot.onrender.com")))
    bot.send_message(message.chat.id, "👋 **Baga nagaan dhuftan!**\n\nDura tikeetii filadhaatii tapha jalqabaa.", reply_markup=markup, parse_mode='Markdown')

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    bot.infinity_polling()
