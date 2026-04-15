import telebot
from flask import Flask
import os
from threading import Thread
import time

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
            .wallet { background: #000; padding: 2px 10px; border-radius: 15px; color: #4caf50; border: 1px solid #4caf50; font-size: 0.9rem; }
            
            /* Ball & History Optimization */
            .ball-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin: 5px auto; }
            .ball { font-size: 22px; color: #ffeb3b; border: 3px solid #0088cc; border-radius: 50%; width: 55px; height: 55px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000; }
            .called-list { display: flex; flex-wrap: wrap; gap: 3px; justify-content: center; padding: 5px; background: #1a1a1a; margin: 5px; border-radius: 8px; min-height: 25px; max-width: 90%; margin-left: auto; margin-right: auto; }
            .called-num { font-size: 0.6rem; background: #333; padding: 1px 4px; border-radius: 3px; color: #888; }
            .called-num.recent { background: #0088cc; color: white; font-weight: bold; }

            /* Small Card Style */
            .cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; padding: 8px; }
            .card { background: #fff; color: #000; border-radius: 6px; overflow: hidden; box-shadow: 0 3px 6px rgba(0,0,0,0.5); }
            .card-header { display: grid; grid-template-columns: repeat(5, 1fr); background: #d32f2f; color: white; font-size: 0.8rem; font-weight: bold; padding: 1px 0; }
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); background: #ccc; gap: 1px; }
            .cell { background: #fff; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; position: relative; }
            .cell.marked::after { content: ""; position: absolute; width: 65%; height: 65%; background: rgba(76, 175, 80, 0.8); border-radius: 50%; }
            .card-footer { background: #eee; font-size: 0.5rem; padding: 1px; color: #666; }

            /* Selection & Spectator */
            .spectator-box { background: #1a1a1a; margin: 10px; padding: 15px; border-radius: 12px; border: 1px dashed #444; }
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 2px; padding: 5px; }
            .t-num { aspect-ratio: 1; background: #222; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 3px; border: 1px solid #333; }
            .t-num.selected { background: #4caf50 !important; color: white; border-color: white; }
            
            #win-overlay { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:2000; flex-direction:column; align-items:center; justify-content:center; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <h2 style="color:#ffeb3b; margin-bottom: 5px;">BINGO! 🏆</h2>
            <p id="win-msg" style="padding: 0 20px;"></p>
            <div style="margin-top: 15px; color: #888; font-size: 0.8rem;">Gara fuula tikeetiitti ofumaan si deebisa...</div>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA</span>
            <div class="wallet">💰 <span id="bal-text">0.00</span></div>
        </div>

        <div id="select-view">
            <div style="padding: 10px; background: #1a1a1a; margin: 10px; border-radius: 10px;">
                <div style="font-size: 0.75rem; color: #888;">Tapha itti aanuuf tikeetii filadhu</div>
                <div style="color: #ffeb3b; font-size: 1.1rem; font-weight: bold;">⏰ <span id="sync-timer">--</span>s</div>
            </div>
            <div class="selection-grid" id="grid-100"></div>
        </div>

        <div id="game-view" style="display:none;">
            <div id="game-info-bar" style="padding: 5px; font-size: 0.75rem; font-weight: bold;"></div>
            
            <div class="ball-container">
                <div class="ball">
                    <span id="b-letter" style="font-size:0.6rem; color:#0088cc;">-</span>
                    <span id="b-num">--</span>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 0.55rem; color: #888;">Lakkofsota waamaman:</div>
                    <div class="called-list" id="called-history"></div>
                </div>
            </div>

            <div id="my-active-section">
                <div class="cards-grid" id="active-cards-ui"></div>
            </div>

            <div id="spectator-section" style="display:none;" class="spectator-box">
                <h4 style="color: #ffeb3b; margin: 0; font-size: 0.9rem;">👀 TAAJJABDII QOFA</h4>
                <p style="font-size: 0.7rem; color: #888; margin: 5px 0;">Tapha itti aanuuf tikeetii filachuu dandeessa.</p>
                <div class="selection-grid" id="grid-spectator"></div>
            </div>
        </div>

        <script>
            let balance = localStorage.getItem('bingo_v21_bal') ? parseFloat(localStorage.getItem('bingo_v21_bal')) : 500.00;
            function updateUI() { document.getElementById('bal-text').innerText = balance.toFixed(2); localStorage.setItem('bingo_v21_bal', balance); }
            updateUI();

            let selectedIDs = [];
            function createGrid(containerId) {
                const container = document.getElementById(containerId);
                container.innerHTML = "";
                for(let i=1; i<=100; i++) {
                    const d = document.createElement('div'); d.className = 't-num'; d.innerText = i;
                    if(selectedIDs.includes(i)) d.classList.add('selected');
                    d.onclick = () => {
                        if(selectedIDs.includes(i)) {
                            selectedIDs = selectedIDs.filter(x => x !== i); d.classList.remove('selected'); balance += 10;
                        } else if(selectedIDs.length < 10 && balance >= 10) {
                            selectedIDs.push(i); d.classList.add('selected'); balance -= 10;
                        }
                        updateUI();
                        document.querySelectorAll('.t-num').forEach(el => {
                            if(parseInt(el.innerText) === i) {
                                selectedIDs.includes(i) ? el.classList.add('selected') : el.classList.remove('selected');
                            }
                        });
                    };
                    container.appendChild(d);
                }
            }
            createGrid('grid-100');

            setInterval(() => {
                let now = Math.floor(Date.now() / 1000);
                let remaining = 60 - (now % 60);
                document.getElementById('sync-timer').innerText = remaining;
                if(remaining === 59) startRound();
            }, 1000);

            let allActiveCards = [], gameStarted = false, calledNums = [];

            function startRound() {
                if(gameStarted) return;
                gameStarted = true;
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                
                if(selectedIDs.length === 0) {
                    document.getElementById('spectator-section').style.display = 'block';
                    document.getElementById('game-info-bar').innerHTML = "🔴 TAPHA DEEMAA JIRU... (Eeggachaa jirta)";
                    createGrid('grid-spectator');
                } else {
                    document.getElementById('game-info-bar').innerHTML = "🟢 HIRMAACHAA JIRTA!";
                }

                for(let id=1; id<=100; id++) {
                    let card = { id: id, nums: genBingo(), marks: new Array(25).fill(false), isMine: selectedIDs.includes(id) };
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
                div.innerHTML = `<div class="card-header"><div>B</div><div>I</div><div>N</div><div>G</div><div>O</div></div><div class="b-grid" id="g-${card.id}"></div><div class="card-footer">ID: #${card.id}</div>`;
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
                    const h = document.getElementById('called-history');
                    h.innerHTML = calledNums.slice(-12).map(n => `<div class="called-num ${n===p?'recent':''}">${n}</div>`).join("");

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
                }, 3000);
            }

            function check(m) {
                const w = [[0,1,2,3,4],[5,6,7,8,9],[10,11,12,13,14],[15,16,17,18,19],[20,21,22,23,24],[0,5,10,15,20],[1,6,11,16,21],[2,7,12,17,22],[3,8,13,18,23],[4,9,14,19,24],[0,6,12,18,24],[4,8,12,16,20]];
                return w.some(p => p.every(i => m[i]));
            }

            function showWin(card) {
                const overlay = document.getElementById('win-overlay');
                overlay.style.display = 'flex';
                const msg = card.isMine ? `BAAY'EE NAMATTI TOLA! Kaartellaan kee #${card.id} mo'ateera!` : `Kaartellaan #${card.id} mo'ateera! (Yeroo itti aanu yaali)`;
                document.getElementById('win-msg').innerText = msg;
                if(card.isMine) { balance += 700; updateUI(); }

                // AUTO-RESTART: Sekondii 5 booda ofumaan gara jalqabaatti deebisa
                setTimeout(() => {
                    location.reload();
                }, 5000);
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
    time.sleep(15)
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=5, timeout=30)
        except Exception as e:
            time.sleep(10)
