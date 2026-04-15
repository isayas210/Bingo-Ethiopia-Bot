import os
import time
import random
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Data user-oota (Ammaaf Memory qofa keessa)
user_wallets = {} # {user_id: balance}

class BingoEngine:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.start_time = time.time()
        self.called_balls = []
        self.called_nums = []
        self.winner_id = None
        self.all_tickets = {}
        # Tikeetii 100 generate gochuu
        for i in range(1, 101):
            ticket = []
            for col in range(5):
                nums = random.sample(range(col*20 + 1, col*20 + 21), 5)
                ticket.append(nums)
            self.all_tickets[str(i)] = ticket

engine = BingoEngine()

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@app.route('/sync')
def sync():
    now = time.time()
    elapsed = now - engine.start_time
    
    if engine.winner_id and elapsed > 20:
        engine.reset_game()
        elapsed = 0

    if 40 < elapsed < 450 and not engine.winner_id:
        target = int((elapsed - 40) // 4)
        while len(engine.called_nums) < target:
            n = random.randint(1, 100)
            if n not in engine.called_nums:
                engine.called_nums.append(n)
                engine.called_balls.append(f"{n}")
    
    return jsonify({
        "elapsed": elapsed, "balls": engine.called_balls,
        "tickets": engine.all_tickets, "winner": engine.winner_id
    })

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; overflow-x: hidden; }
        .stats { background: #001f3f; padding: 10px; border-bottom: 2px solid #ffcc00; position: sticky; top:0; z-index:100; }
        .wallet-bar { background: #111; padding: 8px; display: flex; justify-content: space-around; align-items: center; border-bottom: 1px solid #333; }
        .btn-pay { background: #28a745; border: none; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; padding: 10px; overflow-y: auto; height: calc(100vh - 160px); }
        .card { background: #0a101e; border: 1px solid #00ffcc; border-radius: 8px; padding: 4px; }
        table { width: 100%; border-collapse: collapse; }
        td { border: 1px solid #222; height: 22px; font-size: 11px; background: #1a2a44; font-weight: bold; }
        td.hit { background: #28a745 !important; }
        td.free { background: #ffcc00 !important; color: #000; font-size: 8px; }
    </style>
</head>
<body>
    <div class="stats">
        <div id="status" style="font-size:12px;">Syncing...</div>
        <div style="font-size: 28px; font-weight: bold;" id="ballDisp">?</div>
    </div>
    <div class="wallet-bar">
        <div>Wallet: <span style="color:#ffcc00;">0.00</span> ETB</div>
        <button class="btn-pay" onclick="alert('Gara Bot Admin @BingoEthio_bot deebi'uun kaffaltii Screenshot ergaa.')">Deposit</button>
        <button class="btn-pay" style="background:#dc3545" onclick="alert('Withdraw gochuuf Admin qunnamaa.')">Withdraw</button>
    </div>
    <div class="grid-container" id="my-cards"></div>

<script>
    // Ammaaf tikeetii hunda agarsiisuu (Testing)
    async function sync() {
        try {
            let res = await fetch('/sync');
            let d = await res.json();
            document.getElementById('status').innerText = d.winner ? "WINNER: #" + d.winner : "TAPHNI DEEMAA JIRA";
            document.getElementById('ballDisp').innerText = d.balls.length > 0 ? d.balls[d.balls.length-1] : "?";
            
            const cont = document.getElementById('my-cards');
            if(cont.innerHTML === "") { 
                Object.keys(d.tickets).slice(0, 10).forEach(tid => {
                    let cols = d.tickets[tid];
                    let h = `<div class="card"><div>#${tid}</div><table>`;
                    for(let r=0; r<5; r++) {
                        h += "<tr>";
                        for(let c=0; c<5; c++) {
                            let isF = (c==2 && r==2);
                            h += `<td class="${isF?'free':''}">${isF?'FREE':cols[c][r]}</td>`;
                        }
                        h += "</tr>";
                    }
                    cont.innerHTML += h + "</table></div>";
                });
            }
        } catch(e) {}
    }
    setInterval(sync, 3000);
</script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
