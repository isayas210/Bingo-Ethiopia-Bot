import os
import time
import random
import telebot
from flask import Flask, request, render_template_string, jsonify

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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
        # B:1-20, I:21-40, N:41-60, G:61-80, O:81-100
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

    # Lakkofsa waamuu (Sekondii 40 booda)
    if 40 < elapsed < 450 and not engine.winner_id:
        engine.is_drawing = True
        target_count = int((elapsed - 40) // 4) 
        while len(engine.called_nums) < target_count:
            n = random.randint(1, 100)
            if n not in engine.called_nums:
                engine.called_nums.append(n)
                engine.called_balls.append(f"{get_letter(n)}-{n}")
                
                # Winner check
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
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; overflow-x: hidden; }
        .stats { background: #001f3f; padding: 5px; border-bottom: 2px solid #ffcc00; position: sticky; top:0; z-index:100; height: 85px; }
        .ball { font-size: 26px; font-weight: 900; background: white; color: #001f3f; width: 60px; height: 60px; line-height: 60px; border-radius: 50%; display: inline-block; border: 3px solid #ffcc00; }
        
        #picker { display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; padding: 5px; }
        .p-btn { background: #ffcc00; color: #000; border: 1px solid #fff; padding: 8px 0; border-radius: 3px; font-weight: bold; font-size: 11px; }
        .p-btn.active { background: #28a745 !important; color: white; }

        /* ULTRA COMPACT GRID (Lama lamaan wal biratti) */
        .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px; padding: 5px; }
        .card { background: #0a101e; border: 1px solid #00ffcc; border-radius: 6px; padding: 2px; }
        .card-id { font-size: 8px; color: #00ffcc; margin-bottom: 1px; }
        
        table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        th { color: #ffcc00; font-size: 9px; padding: 0; }
        td { border: 1px solid #222; height: 18px; font-size: 10px; background: #1a2a44; font-weight: bold; }
        td.hit { background: #28a745 !important; }
        td.free { background: #ffcc00 !important; color: #000; font-size: 6px; }
        
        #status { font-size: 12px; font-weight: bold; margin-bottom: 2px; }
    </style>
</head>
<body>
    <div class="stats">
        <div id="status">Syncing...</div>
        <div class="ball" id="ballDisp">?</div>
    </div>

    <div id="selection-view">
        <p id="msg" style="font-size: 12px; margin: 8px;">Tikeetii Kee Kuti:</p>
        <div id="picker"></div>
    </div>

    <div id="game-view" style="display:none;">
        <div id="my-cards" class="grid-container"></div>
    </div>

<script>
    let mySelection = [];
    let isParticipating = false; // Namni sun tapha amma deemaa jiru keessa jiraachuu isaa
    const picker = document.getElementById('picker');
    
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.className = 'p-btn'; b.innerText = i;
        b.onclick = () => {
            if(mySelection.includes(i)) {
                mySelection = mySelection.filter(x => x != i);
                b.classList.remove('active');
            } else {
                mySelection.push(i);
                b.classList.add('active');
            }
        };
        picker.appendChild(b);
    }

    async function sync() {
        try {
            let r = await fetch('/sync');
            let d = await r.json();
            
            // 1. FRESH RESET: Taphni haaraa yoo eegalu
            if(!d.is_drawing && !d.winner && d.elapsed < 5) {
                mySelection = [];
                isParticipating = false;
                document.querySelectorAll('.p-btn').forEach(x => x.classList.remove('active'));
            }

            // 2. CHECK ELIGIBILITY: Namni sun sekondii 40 dura tikeetii kuteeraa?
            if (d.elapsed < 40 && mySelection.length > 0) {
                isParticipating = true;
            }

            // 3. AUTO-VIEW TOGGLE
            if(!d.is_drawing && !d.winner) {
                document.getElementById('status').innerText = "FILANNOO: " + Math.max(0, 40-Math.floor(d.elapsed)) + "s";
                document.getElementById('selection-view').style.display = "block";
                document.getElementById('game-view').style.display = "none";
                document.getElementById('msg').innerText = "Tikeetii Kee Kuti:";
            } else {
                // Yoo tikeetii kuteera ta'e tapha agarsiisi
                if (isParticipating) {
                    document.getElementById('selection-view').style.display = "none";
                    document.getElementById('game-view').style.display = "block";
                    document.getElementById('ballDisp').innerText = d.balls[d.balls.length-1] || "?";
                    if(d.winner) document.getElementById('status').innerText = "🎊 #" + d.winner + " MO'ATE! 🎊";
                    else document.getElementById('status').innerText = "TAPHNI DEEMAA JIRA...";
                    render(d);
                } else {
                    // Yoo tapha keessa hin jirre "Eegi" ittiin jedhi
                    document.getElementById('selection-view').style.display = "block";
                    document.getElementById('game-view').style.display = "none";
                    document.getElementById('msg').innerText = "Taphni amma deemaa jira. Kan biraa hamma eegalutti eegi...";
                    document.getElementById('status').innerText = "EEGI...";
                }
            }
        } catch(e) {}
    }

    function render(d) {
        const cont = document.getElementById('my-cards');
        cont.innerHTML = "";
        mySelection.forEach(tid => {
            let cols = d.tickets[tid.toString()];
            if(!cols) return;
            let h = `<div class="card"><div class="card-id">#${tid}</div>
                <table><thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead><tbody>`;
            for(let r=0; r<5; r++) {
                h += "<tr>";
                for(let c=0; c<5; c++) {
                    let v = cols[c][r];
                    let isFree = (c==2 && r==2);
                    let hit = d.nums.includes(v) || isFree;
                    h += `<td class="${hit?'hit':''} ${isFree?'free':''}">${isFree?'F':v}</td>`;
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
