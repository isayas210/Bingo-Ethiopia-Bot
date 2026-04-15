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

# --- DATABASE SIMULATION ---
# Taphni hundaaf wal-qixa akka deemuuf server irratti qabanna
class BingoEngine:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.called_balls = []
        self.is_drawing = False
        self.winner_id = None
        # Tikeetii 100 guutuu kallaattiin qopheessu
        self.all_tickets = {}
        for i in range(1, 101):
            # Traditional bingo layout: Column 1 (1-20), Col 2 (21-40)...
            ticket = []
            for col in range(5):
                col_nums = random.sample(range(col*20 + 1, col*20 + 21), 5)
                ticket.extend(col_nums)
            self.all_tickets[i] = ticket

engine = BingoEngine()

@app.route('/sync')
def sync():
    now = time.time()
    elapsed = now - engine.start_time
    
    # Reset game every 5 minutes
    if elapsed > 300:
        engine.reset_game()
        elapsed = 0

    if elapsed > 40:
        engine.is_drawing = True
        # Speed: Ball every 3.5 seconds
        target_count = int((elapsed - 40) // 3.5)
        while len(engine.called_balls) < target_count and len(engine.called_balls) < 100:
            n = random.randint(1, 100)
            if n not in engine.called_balls:
                engine.called_balls.append(n)
                # Check for winners immediately on server
                self_check_winners()

    return jsonify({
        "elapsed": elapsed,
        "balls": engine.called_balls,
        "is_drawing": engine.is_drawing,
        "tickets": engine.all_tickets,
        "winner": engine.winner_id
    })

def self_check_winners():
    if engine.winner_id: return
    for tid, nums in engine.all_tickets.items():
        # Check rows
        for r in range(5):
            row = nums[r*5 : r*5+5]
            if all(n in engine.called_balls for n in row):
                engine.winner_id = tid
                return

# --- UI INTERFACE ---
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Ethio Pro</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 5px; }
        .stats { background: #001f3f; padding: 10px; border-bottom: 2px solid #ffcc00; sticky: top; }
        .ball { font-size: 45px; font-weight: bold; background: #fff; color: #000; width: 80px; height: 80px; line-height: 80px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; box-shadow: 0 0 15px #ffcc00; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; padding: 10px; }
        .card { background: #000; border: 1px solid #333; padding: 5px; border-radius: 8px; position: relative; }
        .card.mine { border: 2px solid #00ffcc; box-shadow: 0 0 10px #00ffcc; }
        .card.winner { border: 3px solid #ffcc00; animation: blink 0.5s infinite; }
        @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        td { border: 1px solid #222; height: 25px; background: #1a2a44; }
        td.hit { background: #28a745 !important; color: white; font-weight: bold; }
        .tag { font-size: 9px; position: absolute; top: -8px; left: 5px; background: #ffcc00; color: #000; padding: 2px 5px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="stats">
        <div id="timer">Eeggachaa...</div>
        <div class="ball" id="lastBall">?</div>
    </div>

    <div id="selection" style="padding: 20px;">
        <p>Tikeetii Kee Kuti (1-100):</p>
        <div id="picker" style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px;"></div>
    </div>

    <div id="display" class="grid"></div>

<script>
    let tg = window.Telegram.WebApp;
    let mySelection = [];
    let isDrawing = false;

    // Build Picker
    const p = document.getElementById('picker');
    for(let i=1; i<=100; i++){
        let b = document.createElement('button');
        b.innerText = i;
        b.onclick = () => {
            if(mySelection.includes(i)) mySelection = mySelection.filter(x=>x!=i);
            else mySelection.push(i);
            b.style.background = mySelection.includes(i) ? "#ffcc00" : "";
        };
        p.appendChild(b);
    }

    async function update() {
        let r = await fetch('/sync');
        let d = await r.json();

        if(!d.is_drawing) {
            document.getElementById('timer').innerText = "Tikeetii Kuti: " + Math.max(0, 40-Math.floor(d.elapsed)) + "s";
            document.getElementById('selection').style.display = "block";
            document.getElementById('display').style.display = "none";
        } else {
            document.getElementById('selection').style.display = "none";
            document.getElementById('display').style.display = "grid";
            document.getElementById('lastBall').innerText = d.balls[d.balls.length-1] || "?";
            render(d);
        }
    }

    function render(d) {
        const cont = document.getElementById('display');
        cont.innerHTML = "";
        for(let i=1; i<=100; i++) {
            let isMine = mySelection.includes(i);
            let isWin = d.winner == i;
            let nums = d.tickets[i];
            
            let h = `<div class="card ${isMine?'mine':''} ${isWin?'winner':''}">
                <span class="tag">#${i} ${isMine?'(Kee)':''}</span>
                <table>`;
            for(let row=0; row<5; row++) {
                h += "<tr>";
                for(let col=0; col<5; col++) {
                    let v = nums[row*5 + col];
                    let hit = d.balls.includes(v);
                    h += `<td class="${hit?'hit':''}">${v}</td>`;
                }
                h += "</tr>";
            }
            h += "</table></div>";
            cont.innerHTML += h;
        }
        if(d.winner) {
            let winTxt = mySelection.includes(d.winner) ? "ATTI INJIFATTE! (x100)" : "MANNI MO'ATE!";
            document.getElementById('timer').innerText = "WINNER: #" + d.winner + " - " + winTxt;
        }
    }

    setInterval(update, 3000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bingo Live Ethiopia Pro! Tikeetii kee filadhu.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
