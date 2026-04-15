import telebot
from flask import Flask
import os
from threading import Thread
import time

# Token kee
BOT_TOKEN = "8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Bingo Ethiopia - Gaming Hub</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #000; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .nav-bar { display: flex; justify-content: space-between; padding: 10px; background: #0088cc; border-radius: 0 0 15px 15px; position: sticky; top: 0; z-index: 100; }
            .wallet { color: #4caf50; font-weight: bold; background: #fff; padding: 2px 10px; border-radius: 15px; font-size: 0.9rem; }
            
            #timer-display { font-size: 22px; color: #ffeb3b; margin: 10px; font-weight: bold; }
            
            /* 1-100 Grid */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 8px; background: #111; border-radius: 10px; }
            .t-num { aspect-ratio: 1; background: #f44336; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 3px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; border: 1px solid white; }

            /* Game Area */
            #game-page { display: none; }
            .call-ball { font-size: 30px; color: #ffeb3b; border: 3px solid #0088cc; border-radius: 50%; width: 80px; height: 80px; margin: 15px auto; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #222, #000); }
            
            .all-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 5px; }
            .card-box { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 4px; }
            .card-label { font-size: 0.7rem; color: #0088cc; font-weight: bold; margin-bottom: 3px; }
            
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #333; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 2px; }
            .cell.marked { background: #4caf50 !important; color: white; animation: highlight 0.5s ease; }
            
            @keyframes highlight { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }

            /* Win Popup */
            #win-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 2000; flex-direction: column; align-items: center; justify-content: center; }
            .win-text { font-size: 2.5rem; color: #ffeb3b; font-weight: bold; }
            .btn-reset { margin-top: 20px; padding: 12px 25px; background: #0088cc; color: white; border: none; border-radius: 10px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div id="win-modal">
            <div class="win-text">BINGO! 🏆</div>
            <p>Karteellaa #<span id="win-id">--</span> Injifatteetta!</p>
            <button class="btn-reset" onclick="location.reload()">Tapha Haaraa Jalqabi</button>
        </div>

        <div class="nav-bar">
            <span>BINGO ETHIOPIA</span>
            <div class="wallet">💰 <span id="user-bal">500.00</span></div>
        </div>

        <div id="select-page">
            <div id="timer-display">⏱ <span id="sec">40</span>s</div>
            <p style="font-size: 0.8rem; color: #ccc;">Kaarteellaa filadhu (Gatii: 5 ETB)</p>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-page">
            <div class="call-ball" id="current-call">--</div>
            <div class="all-cards" id="cards-display"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let balance = 500.00;
            let timer = 40;
            let myTickets = [];
            let isOver = false;

            const box = document.getElementById('selection-box');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div');
                d.className = 't-num';
                d.innerText = i;
                d.onclick = function() {
                    if(myTickets.length < 8 || this.classList.contains('selected')) {
                        if(!this.classList.contains('selected')) {
                            if(balance >= 5) {
                                this.classList.add('selected');
                                myTickets.push(i);
                                balance -= 5;
                                updateUI();
                            }
                        } else {
                            this.classList.remove('selected');
                            myTickets = myTickets.filter(n => n !== i);
                            balance += 5;
                            updateUI();
                        }
                    }
                };
                box.appendChild(d);
            }

            function updateUI() { document.getElementById('user-bal').innerText = balance.toFixed(2); }

            const clock = setInterval(() => {
                timer--;
                document.getElementById('sec').innerText = timer;
                if(timer <= 0) {
                    clearInterval(clock);
                    if(myTickets.length > 0) startBingoGame();
                    else location.reload();
                }
            }, 1000);

            function startBingoGame() {
                document.getElementById('select-page').style.display = 'none';
                document.getElementById('game-page').style.display = 'block';
                const display = document.getElementById('cards-display');

                myTickets.forEach(tid => {
                    const wrap = document.createElement('div');
                    wrap.className = 'card-box';
                    wrap.innerHTML = `<div class="card-label">BINGO #${tid}</div>`;
                    const g = document.createElement('div');
                    g.className = 'bingo-grid';
                    g.id = `t-${tid}`;
                    
                    let nums = [];
                    while(nums.length < 25) {
                        let r = Math.floor(Math.random() * 75) + 1;
                        if(!nums.includes(r)) nums.push(r);
                    }

                    nums.forEach((n, i) => {
                        const c = document.createElement('div');
                        c.className = 'cell';
                        c.dataset.val = (i === 12) ? "FREE" : n;
                        c.innerText = c.dataset.val;
                        if(i === 12) c.classList.add('marked');
                        g.appendChild(c);
                    });
                    wrap.appendChild(g);
                    display.appendChild(wrap);
                });
                runCaller();
            }

            function runCaller() {
                const L = ['B', 'I', 'N', 'G', 'O'];
                const run = setInterval(() => {
                    if(isOver) { clearInterval(run); return; }
                    let char = L[Math.floor(Math.random()*5)];
                    let num = Math.floor(Math.random()*75)+1;
                    document.getElementById('current-call').innerText = char + " " + num;

                    document.querySelectorAll('.cell').forEach(cell => {
                        if(cell.dataset.val == num) {
                            cell.classList.add('marked');
                            checkWinner(cell.parentElement);
                        }
                    });
                }, 4000);
            }

            function checkWinner(grid) {
                const cells = Array.from(grid.children);
                const m = cells.map(c => c.classList.contains('marked'));
                let won = false;
                for(let i=0; i<5; i++) {
                    // Sarara hiriiraa (Row)
                    if(m[i*5] && m[i*5+1] && m[i*5+2] && m[i*5+3] && m[i*5+4]) won = true;
                    // Sarara gadii (Column)
                    if(m[i] && m[i+5] && m[i+10] && m[i+15] && m[i+20]) won = true;
                }
                if(won && !isOver) {
                    isOver = true;
                    balance += 150; // Mo'achuu
                    updateUI();
                    document.getElementById('win-modal').style.display = 'flex';
                    document.getElementById('win-id').innerText = grid.id.replace('t-','');
                }
            }
        </script>
    </body>
    </html>
    """

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    time.sleep(2)
    bot.remove_webhook() # Dogoggora Conflict balleessuuf
    bot.polling(none_stop=True)
