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
    # Ofumaan mirkaneessuuf (Auto-verification simulation)
    user_balances[uid] = user_balances.get(uid, 10) + 50
    return jsonify({"new_balance": user_balances[uid]})

@app.route('/api/start_game', methods=['POST'])
def api_start():
    uid = str(request.json.get('user_id'))
    if user_balances.get(uid, 0) < 10:
        return jsonify({"error": "Balance gahaa miti!"}), 400
    user_balances[uid] -= 10
    card = generate_bingo_card()
    raw_drawn = random.sample(range(1, 76), 15)
    labeled_drawn = [get_bingo_label(n) for n in raw_drawn]
    return jsonify({"card": card, "drawn": labeled_drawn, "new_balance": user_balances[uid]})

@app.route('/api/claim_win', methods=['POST'])
def api_win():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 0) + 50
    return jsonify({"new_balance": user_balances[uid]})

# --- FRONTEND (DEPOSIT SCREENSHOT LOGIC) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Bingo Ethiopia Auto-Pay</title>
    <style>
        body { background: #001489; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
        .app-container { border: 2px solid #DBA111; border-radius: 20px; padding: 15px; background: rgba(0,0,0,0.95); min-height: 90vh; }
        .balance-card { background: #000; border: 2px solid #00FF00; padding: 10px; border-radius: 12px; margin-bottom: 15px; }
        .btn { padding: 12px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 8px; }
        .play-btn { background: #DBA111; color: black; font-size: 1.2em; }
        .dep-btn { background: #2ecc71; color: white; }
        .with-btn { background: #e74c3c; color: white; }
        .info-panel { background: #222; padding: 15px; border-radius: 10px; text-align: left; font-size: 0.85em; display: none; margin-bottom: 10px; border: 1px solid #DBA111; }
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 10px; }
        .cell { background: white; color: black; padding: 10px 2px; border-radius: 4px; font-weight: bold; font-size: 0.8em; }
        .cell.called { background: #00FF00; color: white; }
    </style>
</head>
<body>
    <div class="app-container">
        <h2 style="color:#DBA111;">🎰 BINGO ETHIOPIA</h2>
        
        <div class="balance-card">
            <small>BALANCE</small>
            <h3 id="bal-val" style="color:#00FF00; font-size:2em; margin:5px 0;">-- ETB</h3>
        </div>

        <div id="main-menu">
            <button class="btn play-btn" onclick="startGame()">🎮 TAPHA JALQABI</button>
            <button class="btn dep-btn" onclick="toggleDeposit()">💳 DEPOSIT (QARSHII GALCHI)</button>
            
            <div id="deposit-info" class="info-panel">
                <b style="color:#DBA111;">Kaffaltii (Isayas Emana):</b><br>
                📱 Telebirr: 0974085753<br>
                🏦 CBE: 1000659750973<br>
                🔸 CBE Birr: 0974085753<br><br>
                1. Kaffaltii raawwadhu.<br>
                2. Screenshot botaaf ergi.<br>
                3. Erga erganii booda kan gadii xuqi:<br><br>
                <button class="btn" style="background:#00FF00; color:black; padding:5px;" onclick="confirmDep()">✅ MIRKANEESSI (DONE)</button>
            </div>

            <button class="btn with-btn" onclick="requestWithdraw()">💰 WITHDRAW (QARSHII BAASI)</button>
        </div>

        <div id="game-section" style="display:none;">
            <div id="draw-display" style="background:#DBA111; color:black; padding:15px; border-radius:10px; font-weight:bold; font-size:1.5em; margin-bottom:10px;">...</div>
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

        function toggleDeposit() {
            let panel = document.getElementById('deposit-info');
            panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
        }

        async function confirmDep() {
            const res = await fetch('/api/confirm_deposit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
            alert("Mirkanaa'eera! 50 ETB siif dabalameera.");
            toggleDeposit();
        }

        function requestWithdraw() {
            let bal = parseInt(document.getElementById('bal-val').innerText);
            if (bal < 50) { alert("Yoo xiqqaate 50 ETB barbaachisa!"); }
            else { tg.sendData("WITHDRAW_REQUEST_" + bal); tg.close(); }
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
                let label = data.drawn[i];
                let numOnly = label.split('-')[1];
                document.getElementById('draw-display').innerText = label;
                let cell = document.getElementById('c-'+numOnly);
                if(cell) cell.className = 'cell called';
                i++;
            }, 1200);
        }
        window.onload = loadData;
    </script>
</body>
</html>
