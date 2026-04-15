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
        self.user_balances = {} # {chat_id: balance}

    def reset_game(self):
        self.start_time = time.time()
        self.called_balls = []
        self.called_nums = []
        self.is_drawing = False
        self.winner_id = None
        self.all_tickets = {}
        for i in range(1, 101):
            ticket = []
            for col in range(5):
                nums = random.sample(range(col*20 + 1, col*20 + 21), 5)
                ticket.append(nums)
            self.all_tickets[str(i)] = ticket

engine = BingoEngine()

@app.route('/sync')
def sync():
    now = time.time()
    elapsed = now - engine.start_time
    
    # Game Reset Logic
    if engine.winner_id and elapsed > 20:
        engine.reset_game()
        elapsed = 0

    if 40 < elapsed < 300 and not engine.winner_id:
        engine.is_drawing = True
        target = int((elapsed - 40) // 4)
        while len(engine.called_nums) < target:
            n = random.randint(1, 100)
            if n not in engine.called_nums:
                engine.called_nums.append(n)
                engine.called_balls.append(f"{n}") # Simplified for logic
                
                # Check winner
                for tid, cols in engine.all_tickets.items():
                    for r in range(5):
                        if all(((cols[c][r] in engine.called_nums) or (c==2 and r==2)) for c in range(5)):
                            engine.winner_id = tid
                            return jsonify({"winner": tid, "balls": engine.called_balls})

    return jsonify({
        "elapsed": elapsed,
        "balls": engine.called_balls,
        "nums": engine.called_nums,
        "is_drawing": engine.is_drawing,
        "tickets": engine.all_tickets,
        "winner": engine.winner_id
    })

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; }
        .stats { background: #001f3f; padding: 10px; border-bottom: 3px solid #ffcc00; }
        .ball { font-size: 40px; background: white; color: #001f3f; width: 80px; height: 80px; line-height: 80px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; }
        
        /* Picker: Default Yellow */
        #picker { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 10px; }
        .p-btn { background: #ffcc00; color: #000; border: 1px solid #fff; padding: 10px 0; border-radius: 5px; font-weight: bold; }
        .p-btn.selected { background: #28a745 !important; color: white; }

        .card { width: 90%; max-width: 350px; background: #0a101e; border: 3px solid #00ffcc; border-radius: 15px; padding: 15px; margin: 20px auto; }
        table { width: 100%; border-collapse: collapse; }
        th { color: #ffcc00; font-size: 22px; }
        td { border: 1px solid #222; height: 40px; font-size: 18px; background: #1a2a44; }
        td.hit { background: #28a745 !important; }
        td.free { background: #ffcc00 !important; color: #000; font-size: 10px; }
        #balance-display { color: #00ffcc; font-weight: bold; }
    </style>
</head>
<body>
    <div class="stats">
        <div>Balance: <span id="balance-display">1000</span> ETB</div>
        <div id="status">Syncing...</div>
        <div class="ball" id="ballDisp">?</div>
    </div>

    <div id="selection-view">
        <p>Tikeetii Kee Kuti:</p>
        <div id="picker"></div>
    </div>

    <div id="game-view" style="display:none;">
        <div id="my-cards-container"></div>
    </div>

<script>
    let myTickets = [];
    let balance = 1000;

    // Create Picker
    const picker = document.getElementById('picker');
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.className = 'p-btn'; b.id = 'btn-' + i; b.innerText = i;
        b.onclick = () => {
            if(myTickets.includes(i)) {
                myTickets = myTickets.filter(x => x != i);
                b.classList.remove('selected');
            } else {
                myTickets.push(i);
                b.classList.add('selected');
            }
        };
        picker.appendChild(b);
    }

    async function sync() {
        let r = await fetch('/sync');
        let d = await r.json();
        
        if(!d.is_drawing && !d.winner) {
            // New Game Reset
            if(d.elapsed < 5) { 
                myTickets = []; 
                document.querySelectorAll('.p-btn').forEach(b => b.classList.remove('selected'));
            }
            document.getElementById('status').innerText = "Tikeetii Kuti: " + Math.max(0, 40-Math.floor(d.elapsed)) + "s";
            document.getElementById('selection-view').style.display = "block";
            document.getElementById('game-view').style.display = "none";
        } else {
            document.getElementById('selection-view').style.display = "none";
            document.getElementById('game-view').style.display = "block";
            document.getElementById('ballDisp').innerText = d.balls[d.balls.length-1] || "?";
            
            if(d.winner) {
                document.getElementById('status').innerText = "WINNER: #" + d.winner;
                if(myTickets.includes(parseInt(d.winner))) {
                    balance += 500; // Fake win add
                    document.getElementById('balance-display').innerText = balance;
                }
            }
            renderMyTickets(d);
        }
    }

    function renderMyTickets(d) {
        const cont = document.getElementById('my-cards-container');
        cont.innerHTML = "";
        myTickets.forEach(tid => {
            let cols = d.tickets[tid.toString()];
            let h = `<div class="card">
                <div style="margin-bottom:5px;">TIKEETII KEE #${tid}</div>
                <table><thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead><tbody>`;
            for(let r=0; r<5; r++) {
                h += "<tr>";
                for(let c=0; c<5; c++) {
                    let v = cols[c][r];
                    let isFree = (c==2 && r==2);
                    let hit = d.nums.includes(v) || isFree;
                    h += `<td class="${hit?'hit':''} ${isFree?'free':''}">${isFree?'FREE':v}</td>`;
                }
                h += "</tr>";
            }
            h += "</tbody></table></div>";
            cont.innerHTML += h;
        });
    }
    setInterval(sync, 3000);
</script>
</body>
</html>
