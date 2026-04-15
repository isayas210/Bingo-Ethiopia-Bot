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

def get_letter(n):
    if n <= 20: return "B"
    elif n <= 40: return "I"
    elif n <= 60: return "N"
    elif n <= 80: return "G"
    else: return "O"

@app.route('/sync')
def sync():
    now = time.time()
    elapsed = now - engine.start_time
    
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
                engine.called_balls.append(f"{get_letter(n)}-{n}")
                
                for tid, cols in engine.all_tickets.items():
                    for r in range(5):
                        if all(((cols[c][r] in engine.called_nums) or (c==2 and r==2)) for c in range(5)):
                            engine.winner_id = tid
                            return jsonify({"winner": tid, "balls": engine.called_balls})

    return jsonify({
        "elapsed": elapsed, "balls": engine.called_balls, "nums": engine.called_nums,
        "is_drawing": engine.is_drawing, "tickets": engine.all_tickets, "winner": engine.winner_id
    })

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; }
        .stats { background: #001f3f; padding: 10px; border-bottom: 3px solid #ffcc00; position: sticky; top:0; z-index:10; }
        .ball { font-size: 35px; font-weight: bold; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; margin-top:5px; }
        #picker { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; padding: 10px; }
        .p-btn { background: #ffcc00; color: #000; border: 1px solid #fff; padding: 12px 0; border-radius: 5px; font-weight: bold; font-size: 14px; }
        .p-btn.active { background: #28a745 !important; color: white; }
        .card { width: 95%; max-width: 380px; background: #0a101e; border: 3px solid #00ffcc; border-radius: 15px; padding: 10px; margin: 15px auto; }
        table { width: 100%; border-collapse: collapse; }
        th { color: #ffcc00; font-size: 22px; padding: 5px; }
        td { border: 1px solid #222; height: 45px; font-size: 18px; background: #1a2a44; font-weight: bold; }
        td.hit { background: #28a745 !important; }
        td.free { background: #ffcc00 !important; color: #000; font-size: 11px; }
    </style>
</head>
<body>
    <div class="stats">
        <div id="status">Syncing...</div>
        <div class="ball" id="ballDisp">?</div>
    </div>
    <div id="selection">
        <p>Tikeetii Kee Kuti (Keelloo -> Magariisa):</p>
        <div id="picker"></div>
    </div>
    <div id="game" style="display:none;">
        <div id="my-cards"></div>
    </div>
<script>
    let mySelection = [];
    const picker = document.getElementById('picker');
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.className = 'p-btn'; b.innerText = i;
        b.onclick = () => {
            if(mySelection.includes(i)) { mySelection = mySelection.filter(x=>x!=i); b.classList.remove('active'); }
            else { mySelection.push(i); b.classList.add('active'); }
        };
        picker.appendChild(b);
    }
    async function sync() {
        let r = await fetch('/sync');
        let d = await r.json();
        if(!d.is_drawing && !d.winner) {
            if(d.elapsed < 5) { mySelection = []; document.querySelectorAll('.p-btn').forEach(x=>x.classList.remove('active')); }
            document.getElementById('status').innerText = "TIKEETII KUTI: " + Math.max(0, 40-Math.floor(d.elapsed)) + "s";
            document.getElementById('selection').style.display = "block";
            document.getElementById('game').style.display = "none";
        } else {
            document.getElementById('selection').style.display = "none";
            document.getElementById('game').style.display = "block";
            document.getElementById('ballDisp').innerText = d.balls[d.balls.length-1] || "?";
            if(d.winner) document.getElementById('status').innerText = "WINNER: #" + d.winner;
            render(d);
        }
    }
    function render(d) {
        const cont = document.getElementById('my-cards');
        cont.innerHTML = "";
        mySelection.forEach(tid => {
            let cols = d.tickets[tid.toString()];
            let h = `<div class="card"><div style="color:#00ffcc; font-size:12px;">TIKEETII KEE #${tid}</div>
                <table><thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead><tbody>`;
            for(let row=0; row<5; row++) {
                h += "<tr>";
                for(let col=0; col<5; col++) {
                    let v = cols[col][row];
                    let isFree = (col==2 && row==2);
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
"""

@app.route('/')
def index(): return render_template_string(HTML_CONTENT)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bingo Ethiopia! Tikeetii filadhu.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
