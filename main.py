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
    if uid not in user_balances: user_balances[uid] = 20
    return jsonify({"balance": user_balances[uid]})

@app.route('/api/confirm_deposit', methods=['POST'])
def confirm_deposit():
    uid = str(request.json.get('user_id'))
    user_balances[uid] = user_balances.get(uid, 20) + 50
    return jsonify({"new_balance": user_balances[uid]})

@app.route('/api/start_game', methods=['POST'])
def api_start():
    uid = str(request.json.get('user_id'))
    selected_tickets = request.json.get('tickets', [])
    count = len(selected_tickets)
    cost = count * 10
    
    if count == 0:
        return jsonify({"error": "Maaloo dura tikeetii filadhaa!"}), 400
    if user_balances.get(uid, 0) < cost:
        return jsonify({"error": f"Balance gahaa miti! Tikeetii {count}-f {cost} ETB barbaachisa."}), 400
    
    user_balances[uid] -= cost
    all_cards = [generate_bingo_card() for _ in range(count)]
    raw_drawn = random.sample(range(1, 76), 40) 
    labeled_drawn = [get_bingo_label(n) for n in raw_drawn]
    
    return jsonify({
        "cards": all_cards, 
        "drawn": labeled_drawn, 
        "new_balance": user_balances[uid],
        "ticket_numbers": selected_tickets
    })

# --- FRONTEND (GRID SELECTION 1-100) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <title>Bingo Ethiopia Pro</title>
    <style>
        body { background: #001489; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
        .app-container { border: 2px solid #DBA111; border-radius: 20px; padding: 15px; background: rgba(0,0,0,0.95); min-height: 90vh; }
        .balance-card { background: #000; border: 2px solid #00FF00; padding: 10px; border-radius: 12px; margin-bottom: 15px; }
        .btn { padding: 12px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 8px; }
        
        /* 1-100 Grid Selection */
        .grid-100 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; max-height: 250px; overflow-y: auto; background: #111; padding: 10px; border-radius: 10px; border: 1px solid #444; }
        .t-num { background: #333; color: white; border: 1px solid #555; padding: 10px 0; border-radius: 5px; font-size: 0.9em; cursor: pointer; }
        .t-num.selected { background: #DBA111; color: black; border-color: white; font-weight: bold; }
        
        .card-container { background: #222; margin-top: 15px; padding: 10px; border-radius: 10px; border-left: 5px solid #DBA111; }
        .card-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 5px; }
        .cell { background: white; color: black; padding: 8px 1px; border-radius: 4px; font-weight: bold; font-size: 0.75em; }
        .cell.called { background: #00FF00; color: white; }
        
        #draw-display { background: #DBA111; color: black; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 1.8em; margin-bottom: 10px; position: sticky; top: 5px; z-index: 100; }
        .history-box { background: #111; padding: 8px; border-radius: 8px; font-size: 0.7em; color: #00FF00; margin-bottom: 10px; max-height: 40px; overflow-y: auto; text-align: left; border: 1px solid #444; }
    </style>
</head>
<body>
    <div class="app-container">
        <h2 style="color:#DBA111;">🎰 BINGO ETHIOPIA</h2>

        <div class="balance-card">
            <small>BALANCE</small>
            <h3 id="bal-val" style="color:#00FF00; font-size:2em; margin:5px 0;">-- ETB</h3>
        </div>

        <div id="selection-stage">
            <p style="margin-bottom:10px;">Tikeetiiwwan 1-100 keessaa filadhu:</p>
            <div class="grid-100" id="ticket-grid"></div>
            <div style="background:#111; margin:15px 0; padding:10px; border-radius:10px;">
                <span id="count-label">Tikeetii: 0</span> | 
                <span id="price-label" style="color:#DBA111;">Gatii: 0 ETB</span>
            </div>
            <button class="btn" style="background:#DBA111; color:black; font-size:1.1em;" onclick="startGame()">🎮 TAPHA JALQABI</button>
        </div>

        <div id="game-section" style="display:none;">
            <div id="draw-display">...</div>
            <div class="history-box" id="history">Kuusaa: </div>
            <div id="cards-wrapper"></div>
        </div>

        <div id="footer-menu" style="margin-top:20px;">
            <button class="btn" style="background:#2ecc71; color:white;" onclick="toggleDeposit()">💳 DEPOSIT</button>
            <div id="deposit-info" style="display:none; background:#222; padding:15px; border-radius:10px; text-align:left; border:1px solid #DBA111;">
                📱 Telebirr: 0974085753<br>
                👤 Isayas Emana<br><br>
                Screenshot Upload:<br>
                <input type="file" id="ss-file" accept="image/*"><br><br>
                <button class="btn" style="background:#00FF00; color:black;" onclick="confirmDep()">✅ MIRKANEESSI</button>
            </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let uid = tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : "123";
        let selectedTickets = [];

        // 1-100 Grid uumuu
        const grid = document.getElementById('ticket-grid');
        for(let i=1; i<=100; i++) {
            let d = document.createElement('div');
            d.className = 't-num';
            d.innerText = i;
            d.onclick = function() {
                if(selectedTickets.includes(i)) {
                    selectedTickets = selectedTickets.filter(t => t !== i);
                    this.classList.remove('selected');
                } else {
                    if(selectedTickets.length >= 20) { alert("Max 20 tikeetii qofa!"); return; }
                    selectedTickets.push(i);
                    this.classList.add('selected');
                }
                updateLabels();
            };
            grid.appendChild(d);
        }

        function updateLabels() {
            document.getElementById('count-label').innerText = "Tikeetii: " + selectedTickets.length;
            document.getElementById('price-label').innerText = "Gatii: " + (selectedTickets.length * 10) + " ETB";
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

        async function startGame() {
            if(selectedTickets.length === 0) { alert("Maaloo dura tikeetii filadhaa!"); return; }
            
            const res = await fetch('/api/start_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid, tickets: selectedTickets })
            });
            const data = await res.json();
            if(data.error) { alert(data.error); return; }

            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
            document.getElementById('selection-stage').style.display = "none";
            document.getElementById('footer-menu').style.display = "none";
            document.getElementById('game-section').style.display = "block";
            
            const wrapper = document.getElementById('cards-wrapper');
            wrapper.innerHTML = "";
            data.cards.forEach((card, idx) => {
                let cardDiv = document.createElement('div');
                cardDiv.className = 'card-container';
                cardDiv.innerHTML = `<small>Tikeetii #${data.ticket_numbers[idx]}</small>`;
                let gridDiv = document.createElement('div');
                gridDiv.className = 'card-grid';
                for(let r=0; r<5; r++){
                    for(let c=0; c<5; c++){
                        let val = card[c][r];
                        let d = document.createElement('div');
                        d.className = 'cell'; d.innerText = val;
                        d.id = `t${idx}-v${val}`;
                        gridDiv.appendChild(d);
                    }
                }
                cardDiv.appendChild(gridDiv);
                wrapper.appendChild(cardDiv);
            });

            let i = 0;
            let historyArr = [];
            let timer = setInterval(() => {
                if(i >= data.drawn.length) {
                    clearInterval(timer);
                    document.getElementById('draw-display').innerText = "XUMURE!";
                    return;
                }
                let label = data.drawn[i];
                let numOnly = label.split('-')[1];
                document.getElementById('draw-display').innerText = label;
                historyArr.push(label);
                document.getElementById('history').innerText = "Kuusaa: " + historyArr.join(", ");
                
                data.cards.forEach((_, idx) => {
                    let cell = document.getElementById(`t${idx}-v${numOnly}`);
                    if(cell) cell.classList.add('called');
                });
                i++;
            }, 1400);
        }

        function toggleDeposit() {
            let d = document.getElementById('deposit-info');
            d.style.display = d.style.display === 'none' ? 'block' : 'none';
        }

        async function confirmDep() {
            if(!document.getElementById('ss-file').files[0]) { alert("Dura screenshot filadhaa!"); return; }
            const res = await fetch('/api/confirm_deposit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: uid })
            });
            const data = await res.json();
            document.getElementById('bal-val').innerText = data.new_balance + " ETB";
            alert("Mirkanaa'eera!");
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
    bot.send_message(message.chat.id, "👋 **Baga nagaan dhuftan!**\n\nBingo Ethiopia irratti lakkoofsa tikeetii 1-100 keessaa kan barbaaddan filattanii taphachuu dandeessu.", reply_markup=markup, parse_mode='Markdown')

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    bot.infinity_polling()
