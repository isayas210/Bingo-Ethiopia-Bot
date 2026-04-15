import telebot
from flask import Flask
import os
from threading import Thread
import time

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
            body { background-color: #0b0b0b; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 0; overflow-x: hidden; }
            .nav { display: flex; justify-content: space-between; background: #0088cc; padding: 10px; font-weight: bold; position: sticky; top: 0; z-index: 100; }
            .wallet { background: #000; padding: 2px 10px; border-radius: 15px; color: #4caf50; border: 1px solid #4caf50; font-size: 0.85rem; }
            .ball-container { display: flex; align-items: center; justify-content: center; gap: 8px; margin: 5px auto; }
            .ball { font-size: 20px; color: #ffeb3b; border: 3px solid #0088cc; border-radius: 50%; width: 50px; height: 50px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000; }
            .called-list { display: flex; flex-wrap: wrap; gap: 2px; justify-content: center; padding: 5px; background: #1a1a1a; margin: 5px auto; border-radius: 8px; min-height: 20px; max-width: 95%; }
            .called-num { font-size: 0.6rem; background: #333; padding: 1px 3px; border-radius: 2px; color: #888; }
            .called-num.recent { background: #0088cc; color: white; font-weight: bold; }
            .cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 6px; padding: 5px; }
            .card { background: #fff; color: #000; border-radius: 5px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
            .card-header { display: grid; grid-template-columns: repeat(5, 1fr); background: #d32f2f; color: white; font-size: 0.75rem; font-weight: bold; padding: 1px 0; }
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); background: #ccc; gap: 1px; }
            .cell { background: #fff; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: bold; position: relative; }
            .cell.marked::after { content: ""; position: absolute; width: 60%; height: 60%; background: rgba(76, 175, 80, 0.8); border-radius: 50%; }
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; padding: 5px; }
            .t-num { aspect-ratio: 1; background: #222; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; border-radius: 2px; border: 1px solid #333; }
            .t-num.selected { background: #4caf50 !important; color: white; }
            #win-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:2000; flex-direction:column; align-items:center; justify-content:center; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <h2 style="color:#ffeb3b; margin:0;">BINGO! 🏆</h2>
            <p id="win-msg" style="font-size: 0.9rem; padding: 10px;"></p>
            <div style="color: #4caf50; font-size: 0.75rem;">Sekondii 2 booda ofumaan deebi'a...</div>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA</span>
            <div class="wallet">💰 <span id="bal-text">0.00</span></div>
        </div>

        <div id="select-view">
            <div style="padding: 8px; background: #1a1a1a; margin: 8px; border-radius: 8px;">
                <div style="font-size: 0.7rem; color: #888;">Tapha itti aanuuf tikeetii filadhu (Sekondii 30)</div>
                <div style="color: #ffeb3b; font-size: 1.2rem; font-weight: bold;">⏰ <span id="sync-timer">--</span>s</div>
            </div>
            <div class="selection-grid" id="grid-100"></div>
        </div>

        <div id="game-view" style="display:none;">
            <div class="ball-container">
                <div class="ball">
                    <span id="b-letter" style="font-size:0.5rem; color:#0088cc;">-</span>
                    <span id="b-num">--</span>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 0.5rem; color: #888;">Seenaa:</div>
                    <div class="called-list" id="called-history"></div>
                </div>
            </div>
            <div class="cards-grid" id="active-cards-ui"></div>
        </div>

        <script>
            let balance = localStorage.getItem('bingo_v23_bal') ? parseFloat(localStorage.getItem('bingo_v23_bal')) : 500.00;
            function updateUI() { document.getElementById('bal-text').innerText = balance.toFixed(2); localStorage.setItem('bingo_v23_bal', balance); }
            updateUI();

            let selectedIDs = [];
            function createGrid() {
                const container = document.getElementById('grid-100');
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
                    container.appendChild(d);
                }
            }
            createGrid();

            // TIMER SIIRREEFFAME (SEKONDII 30)
            setInterval(() => {
                let now = Math.floor(Date.now() / 1000);
                let remaining = 30 - (now % 30);
                document.getElementById('sync-timer').innerText = remaining;
                if(remaining === 29 && !gameStarted) startRound();
            }, 1000);

            let allActiveCards = [], gameStarted = false, calledNums = [];

            function startRound() {
                gameStarted = true;
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                let mySelection = [...selectedIDs];
                selectedIDs = [];

                for(let id=1; id<=100; id++) {
                    let card = { id: id, nums: genBingo(), marks: new Array(25).fill(false), isMine: mySelection.includes(id) };
                    card.marks[12] = true;
                    allActiveCards.push(card);
                    if(card.isMine) renderCard(card);
                }
                runGame();
            }

            function genBingo() {
                let c = [];
                for(let i=0; i<5; i++) {
                    let r = Array.from({length:15}, (_,j)=>(i*15)+j+1);
                    let col = []; for(let k=0; k<5; k++) col.push(r.splice(Math.floor(Math.random()*r.length),1)[0]);
                    c.push(col);
                }
                let flat = []; for(let r=0; r<5; r++) { for(let cl=0; cl<5; cl++) flat.push(c[cl][r]); }
                return flat;
            }

            function renderCard(card) {
                const div = document.createElement('div'); div.className = 'card';
                div.innerHTML = `<div class="card-header"><div>B</div><div>I</div><div>N</div><div>G</div><div>O</div></div><div class="b-grid" id="g-${card.id}"></div>`;
                document.getElementById('active-cards-ui').appendChild(div);
                card.nums.forEach((n, i) => {
                    const cell = document.createElement('div'); cell.className = 'cell'; cell.id = `c-${card.id}-${i}`;
                    cell.innerText = (i===12) ? "FREE" : n;
                    if(i===12) cell.classList.add('marked');
                    document.getElementById(`g-${card.id}`).appendChild(cell);
                });
            }

            function runGame() {
                let pool = Array.from({length:75}, (_,i)=>i+1);
                const loop = setInterval(() => {
                    if(pool.length===0) { clearInterval(loop); return; }
                    let p = pool.splice(Math.floor(Math.random()*pool.length), 1)[0];
                    calledNums.push(p);
                    document.getElementById('b-letter').innerText = "BINGO"[Math.floor((p-1)/15)];
                    document.getElementById('b-num').innerText = p;
                    document.getElementById('called-history').innerHTML = calledNums.slice(-10).map(n => `<div class="called-num ${n===p?'recent':''}">${n}</div>`).join("");

                    allActiveCards.forEach(card => {
                        let idx = card.nums.indexOf(p);
                        if(idx !== -1) {
                            card.marks[idx] = true;
                            if(card.isMine) {
                                let el = document.getElementById(`c-${card.id}-${idx}`);
                                if(el) el.classList.add('marked');
                            }
                        }
                        if(check(card.marks)) { clearInterval(loop); showWin(card); }
                    });
                }, 2000);
            }

            function check(m) {
                const w = [[0,1,2,3,4],[5,6,7,8,9],[10,11,12,13,14],[15,16,17,18,19],[20,21,22,23,24],[0,5,10,15,20],[1,6,11,16,21],[2,7,12,17,22],[3,8,13,18,23],[4,9,14,19,24],[0,6,12,18,24],[4,8,12,16,20]];
                return w.some(p => p.every(i => m[i]));
            }

            function showWin(card) {
                const overlay = document.getElementById('win-overlay');
                overlay.style.display = 'flex';
                document.getElementById('win-msg').innerText = card.isMine ? `MO'ATTAATTA! Kaartellaan #${card.id} mo'ateera!` : `Kaartellaan #${card.id} mo'ateera!`;
                if(card.isMine) { balance += 700; updateUI(); }
                
                // SEKONDII 2 BOODA DEEBISUU
                setTimeout(() => { location.reload(); }, 2000);
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
    t.daemon = True
    t.start()
    
    # Conflict Fix: Sekondii 25 eeggannoo
    time.sleep(25)
    
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception:
            time.sleep(10)
