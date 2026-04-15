import os
import time
import random
import telebot
from flask import Flask, request, render_template_string, jsonify
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

class BingoEngine:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.called_balls = [] # Store as strings like "B-23"
        self.called_nums_only = []
        self.is_drawing = False
        self.winner_id = None
        self.all_tickets = {}
        for i in range(1, 101):
            ticket = []
            # B:1-20, I:21-40, N:41-60, G:61-80, O:81-100
            for col in range(5):
                col_nums = random.sample(range(col*20 + 1, col*20 + 21), 5)
                ticket.append(col_nums)
            self.all_tickets[i] = ticket

engine = BingoEngine()

def get_letter(n):
    if n <= 20: return "B"
    elif n <= 40: return "I"
    elif n <= 60: return "N"
    elif n <= 80: return "G"
    else: return "O"

def check_server_winner():
    if engine.winner_id: return
    for tid, cols in engine.all_tickets.items():
        # Check rows (5 rows total)
        for r in range(5):
            row_match = 0
            for c in range(5):
                num = cols[c][r]
                # Center is Free
                if (c == 2 and r == 2) or (num in engine.called_nums_only):
                    row_match += 1
            if row_match == 5:
                engine.winner_id = tid
                return

@app.route('/sync')
def sync():
    now = time.time()
    elapsed = now - engine.start_time
    
    # If winner found, wait 10s then reset
    if engine.winner_id and elapsed > 10:
        engine.reset_game()
        elapsed = 0

    if 40 < elapsed < 300 and not engine.winner_id:
        engine.is_drawing = True
        target_count = int((elapsed - 40) // 4) # Slowed to 4s for better UX
        while len(engine.called_nums_only) < target_count and len(engine.called_nums_only) < 100:
            n = random.randint(1, 100)
            if n not in engine.called_nums_only:
                engine.called_nums_only.append(n)
                engine.called_balls.append(f"{get_letter(n)}-{n}")
                check_server_winner()

    return jsonify({
        "elapsed": elapsed,
        "balls": engine.called_balls,
        "nums": engine.called_nums_only,
        "is_drawing": engine.is_drawing,
        "tickets": engine.all_tickets,
        "winner": engine.winner_id
    })

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethio</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 5px; }
        .stats { background: #001f3f; padding: 10px; border-bottom: 3px solid #ffcc00; position: sticky; top: 0; z-index: 100; }
        .ball { font-size: 35px; font-weight: 900; background: #fff; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; display: inline-block; border: 5px solid #ffcc00; margin-top: 5px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 15px; padding: 15px; }
        .card { background: #000; border: 1px solid #333; border-radius: 10px; padding: 5px; position: relative; }
        .card.mine { border: 2px solid #00ffcc; box-shadow: 0 0 10px #00ffcc; }
        .card.winner { border: 3px solid #ffcc00; animation: pulse 1s infinite; }
        @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.03);} 100% {transform: scale(1);} }
        table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        th { color: #ffcc00; font-size: 18px; padding: 2px; }
        td { border: 1px solid #222; height: 30px; font-size: 14px; background: #1a2a44; font-weight: bold; }
        td.hit { background: #28a745 !important; color: white; }
        td.free { background: #ffcc00 !important; color: #000; font-size: 10px; }
        .tag { font-size: 10px; background: #333; padding: 2px 6px; border-radius: 4px; margin-bottom: 4px; display: inline-block; }
    </style>
</head>
<body>
    <div class="stats">
        <div id="status">Eeggachaa...</div>
        <div class="ball" id="ballDisplay">?</div>
    </div>

    <div id="selection-screen" style="padding: 20px;">
        <p>Tikeetii Kee Kuti (1-100):</p>
        <div id="picker" style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px;"></div>
    </div>

    <div id="game-screen" class="grid" style="display:none;"></div>

<script>
    let myTickets = [];
    let isDrawing = false;

    // Build 1-100 Picker
    const picker = document.getElementById('picker');
    for(let i=1; i<=100; i++) {
        let btn = document.createElement('button');
        btn.innerText = i;
        btn.style.padding = "10px 0";
        btn.onclick = () => {
            if(myTickets.includes(i)) { myTickets = myTickets.filter(x=>x!=i); btn.style.background = ""; }
            else { myTickets.push(i); btn.style.background = "#ffcc00"; }
        };
        picker.appendChild(btn);
    }

    async function sync() {
        let r = await fetch('/sync');
        let d = await r.json();

        if(!d.is_drawing && !d.winner) {
            document.getElementById('status').innerText = "Tikeetii Kuti: " + Math.max(0, 40-Math.floor(d.elapsed)) + "s";
            document.getElementById('selection-screen').style.display = "block";
            document.getElementById('game-screen').style.display = "none";
        } else {
            document.getElementById('selection-screen').style.display = "none";
            document.getElementById('game-screen').style.display = "grid";
            document.getElementById('ballDisplay').innerText = d.balls[d.balls.length-1] || "?";
            if(d.winner) document.getElementById('status').innerText = "🎊 TIKEETII #" + d.winner + " MO'ATE! 🎊";
            else document.getElementById('status').innerText = "TAPHNI DEEMAA JIRA...";
            render(d);
        }
    }

    function render(d) {
        const cont = document.getElementById('game-screen');
        cont.innerHTML = "";
        for(let i=1; i<=100; i++) {
            let isMine = myTickets.includes(i);
            let isWin = d.winner == i;
            let cols = d.tickets[i]; // Array of 5 columns
            
            let h = `<div class="card ${isMine?'mine':''} ${isWin?'winner':''}">
                <span class="tag">#${i} ${isMine?'(Kee)':''}</span>
                <table>
                    <thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead>
                    <tbody>`;
            for(let row=0; row<5; row++) {
                h += "<tr>";
                for(let col=0; col<5; col++) {
                    let v = cols[col][row];
                    let isFree = (col == 2 && row == 2);
                    let hit = d.nums.includes(v) || isFree;
                    h += `<td class="${hit?'hit':''} ${isFree?'free':''}">${isFree?'FREE':v}</td>`;
                }
                h += "</tr>";
            }
            h += "</tbody></table></div>";
            cont.innerHTML += h;
        }
    }

    setInterval(sync, 3000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bingo Ethiopia Pro! Tikeetii kee filadhu.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
