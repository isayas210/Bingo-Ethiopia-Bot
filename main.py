import telebot
from flask import Flask
import os
from threading import Thread
import time
import random

# BOT TOKEN
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
        <title>Bingo Ethiopia Live</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #0b0b0b; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 0; }
            .nav { display: flex; justify-content: space-between; background: #0088cc; padding: 15px; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
            .wallet { background: #000; padding: 2px 15px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; }
            
            #status-bar { background: #1a1a1a; padding: 10px; margin: 10px; border-radius: 12px; border: 1px solid #333; }
            .timer-txt { color: #ffeb3b; font-size: 1.4rem; font-weight: bold; }
            
            /* Selection Grid */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; padding: 15px; }
            .t-num { aspect-ratio: 1; background: #222; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; border-radius: 6px; border: 1px solid #333; }
            .t-num.selected { background: #4caf50 !important; border-color: white; transform: scale(1.1); }
            
            /* Game View */
            #game-view { display: none; padding: 10px; }
            .ball-container { position: relative; width: 120px; height: 120px; margin: 20px auto; }
            .ball { font-size: 40px; color: #ffeb3b; border: 6px solid #0088cc; border-radius: 50%; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle at 30% 30%, #222, #000); box-shadow: 0 0 20px rgba(0,136,204,0.5); }
            
            /* Traditional Card Style */
            .cards-grid { display: grid; grid-template-columns: 1fr; gap: 20px; max-width: 400px; margin: auto; }
            .card { background: #fff; color: #000; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.8); }
            .card-header { display: grid; grid-template-columns: repeat(5, 1fr); background: #d32f2f; color: white; font-size: 1.5rem; font-weight: 900; padding: 5px 0; }
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); background: #000; gap: 1px; border: 1px solid #000; }
            .cell { background: #fff; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; position: relative; }
            .cell.marked::after { content: ""; position: absolute; width: 80%; height: 80%; background: rgba(76, 175, 80, 0.7); border-radius: 50%; }
            .card-footer { background: #eee; font-size: 0.7rem; padding: 3px; color: #666; }

            /* Win Overlay */
            #win-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:2000; flex-direction:column; align-items:center; justify-content:center; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <h1 style="color:#ffeb3b; font-size:3rem;">BINGO! 🏆</h1>
            <p id="win-msg" style="font-size:1.2rem;"></p>
            <h2 style="color:#4caf50; font-size: 2.5rem;">💰 +700.00 ETB</h2>
            <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:15px 40px; border-radius:15px; font-size:1.2rem; margin-top:20px;">Tapha Haaraa</button>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA LIVE</span>
            <div class="wallet">💰 <span id="bal-text">0.00</span></div>
        </div>

        <div id="select-view">
            <div id="status-bar">
                <div id="state-msg" style="color:#888;">Tapha itti aanuuf tikeetii filadhu (10 ETB)</div>
                <div class="timer-txt">⏰ <span id="sync-timer">--</span>s</div>
            </div>
            <div class="selection-grid" id="grid-100"></div>
        </div>

        <div id="game-view">
            <div id="game-status" style="color:#4caf50; font-weight:bold;">🔴 TAPHA DEEMAA JIRU...</div>
            <div class="ball-container">
                <div class="ball" id="ball-call">
                    <span id="b-letter" style="font-size:1rem; color:#0088cc;">-</span>
                    <span id="b-num">--</span>
                </div>
            </div>
            <div class="cards-grid" id="active-cards-ui"></div>
        </div>

        <script>
            let balance = localStorage.getItem('bingo_v19_bal') ? parseFloat(localStorage.getItem('bingo_v19_bal')) : 500.00;
            function updateUI() { document.getElementById('bal-text').innerText = balance.toFixed(2); localStorage.setItem('bingo_v19_bal', balance); }
            updateUI();

            // 1. Grid 1-100 uumuun
            const grid = document.getElementById('grid-100');
            let selectedIDs = [];
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div'); d.className = 't-num'; d.innerText = i;
                d.onclick = () => {
                    if(selectedIDs.includes(i)) {
                        selectedIDs = selectedIDs.filter(x => x !== i); d.classList.remove('selected'); balance += 10;
                    } else if(selectedIDs.length < 10 && balance >= 10) {
                        selectedIDs.push(i); d.classList.add('selected'); balance -= 10;
                    }
                    updateUI();
                };
                grid.appendChild(d);
            }

            // 2. Timer System (Sync with Server time)
            setInterval(() => {
                let now = Math.floor(Date.now() / 1000);
                let remaining = 60 - (now % 60);
                document.getElementById('sync-timer').innerText = remaining;
                if(remaining === 59) startRound();
            }, 1000);

            let allActiveCards = []; 
            let gameStarted = false;

            function startRound() {
                if(gameStarted) return;
                gameStarted = true;
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                
                // Kaartellaa 1-100 hunda ofumaan uumuu (System-Level)
                for(let id=1; id<=100; id++) {
                    let card = { id: id, nums: generateTraditionalBingo(), marks: new Array(25).fill(false), isMine: selectedIDs.includes(id) };
                    card.marks[12] = true; // FREE Space
                    allActiveCards.push(card);
                    
                    if(card.isMine) renderCardUI(card);
                }
                runBingoGame();
            }

            function generateTraditionalBingo() {
                let card = [];
                let columns = [[],[],[],[],[]];
                for(let i=0; i<5; i++) {
                    let range = Array.from({length: 15}, (_, j) => (i*15) + j + 1);
                    for(let k=0; k<5; k++) {
                        let pick = range.splice(Math.floor(Math.random()*range.length), 1)[0];
                        columns[i].push(pick);
                    }
                }
                // Convert columns to flat 25 array
                for(let r=0; r<5; r++) { for(let c=0; c<5; c++) card.push(columns[c][r]); }
                return card;
            }

            function renderCardUI(card) {
                const div = document.createElement('div'); div.className = 'card';
                div.innerHTML = `
                    <div class="card-header"><div>B</div><div>I</div><div>N</div><div>G</div><div>O</div></div>
                    <div class="b-grid" id="grid-${card.id}"></div>
                    <div class="card-footer">TICKET ID: #${card.id} (SANKAA KEETII)</div>
                `;
                document.getElementById('active-cards-ui').appendChild(div);
                card.nums.forEach((n, idx) => {
                    const c = document.createElement('div'); c.className = 'cell'; c.id = `cell-${card.id}-${idx}`;
                    c.innerText = (idx === 12) ? "FREE" : n;
                    if(idx === 12) c.classList.add('marked');
                    document.getElementById(`grid-${card.id}`).appendChild(c);
                });
            }

            function runBingoGame() {
                let ballPool = Array.from({length: 75}, (_, i) => i + 1);
                const loop = setInterval(() => {
                    if(ballPool.length === 0) { clearInterval(loop); return; }
                    let picked = ballPool.splice(Math.floor(Math.random()*ballPool.length), 1)[0];
                    
                    // Show Ball UI
                    let letter = "BINGO"[Math.floor((picked-1)/15)];
                    document.getElementById('b-letter').innerText = letter;
                    document.getElementById('b-num').innerText = picked;

                    // Check All 100 Cards
                    allActiveCards.forEach(card => {
                        let idx = card.nums.indexOf(picked);
                        if(idx !== -1) {
                            card.marks[idx] = true;
                            if(card.isMine) document.getElementById(`cell-${card.id}-${idx}`).classList.add('marked');
                        }
                        
                        if(checkBingo(card.marks)) {
                            clearInterval(loop);
                            showWinner(card);
                        }
                    });
                }, 3000);
            }

            function checkBingo(m) {
                const wins = [
                    [0,1,2,3,4],[5,6,7,8,9],[10,11,12,13,14],[15,16,17,18,19],[20,21,22,23,24], // Horiz
                    [0,5,10,15,20],[1,6,11,16,21],[2,7,12,17,22],[3,8,13,18,23],[4,9,14,19,24], // Vert
                    [0,6,12,18,24],[4,8,12,16,20] // Diag
                ];
                return wins.some(pattern => pattern.every(i => m[i]));
            }

            function showWinner(card) {
                document.getElementById('win-overlay').style.display = 'flex';
                document.getElementById('win-msg').innerText = card.isMine ? `Baay'ee namatti tola! Kaartellaan kee #${card.id} mo'ateera!` : `Kaartellaan #${card.id} mo'ateera! (Yeroo itti aanu yaali)`;
                if(card.isMine) { balance += 700; updateUI(); }
            }
        </script>
    </body>
    </html>
    """

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    print("Conflict prevention delay...")
    time.sleep(15)

    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=5, timeout=30)
        except Exception as e:
            time.sleep(10)
