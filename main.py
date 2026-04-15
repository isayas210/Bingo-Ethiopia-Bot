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
            body { background-color: #0b0b0b; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .nav { display: flex; justify-content: space-between; background: #0088cc; padding: 12px; border-radius: 0 0 15px 15px; font-weight: bold; }
            .wallet { background: #000; padding: 2px 12px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; }
            
            #status-bar { background: #1a1a1a; padding: 10px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; }
            .timer-txt { color: #ffeb3b; font-size: 1.2rem; font-weight: bold; }
            
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 10px; background: #1a1a1a; border-radius: 12px; }
            .t-num { aspect-ratio: 1; background: #333; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 4px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; border: 1px solid white; }
            
            #game-view { display: none; }
            .ball { font-size: 45px; color: #ffeb3b; border: 5px solid #0088cc; border-radius: 50%; width: 100px; height: 100px; margin: 15px auto; display: flex; align-items: center; justify-content: center; background: #000; box-shadow: 0 0 15px #0088cc; }
            
            .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 5px; }
            .card { background: #151515; border: 1px solid #333; border-radius: 10px; padding: 8px; opacity: 0.5; }
            .card.active { opacity: 1; border-color: #4caf50; }
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #262626; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 3px; }
            .cell.marked { background: #4caf50 !important; }

            #win-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <div style="background: #1a1a1a; padding: 35px; border-radius: 25px; border: 2px solid #ffeb3b; width: 85%;">
                <h1 style="color:#ffeb3b;">BINGO! 🏆</h1>
                <p>Kaarteellaa #<span id="win-id">--</span> mo'ateera!</p>
                <h2 style="color:#4caf50; font-size: 2.2rem;">💰 +700.00 ETB</h2>
                <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:12px 30px; border-radius:12px; font-weight:bold;">Tikeetii Haaraa</button>
            </div>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA LIVE</span>
            <div class="wallet">💰 <span id="bal-text">---</span></div>
        </div>

        <div id="select-view">
            <div id="status-bar">
                <div id="state-msg" style="font-size: 0.9rem; color: #888;">Tapha itti aanuuf tikeetii filadhu</div>
                <div class="timer-txt">⏰ <span id="sync-timer">--</span>s</div>
            </div>
            <div class="selection-grid" id="grid-100"></div>
        </div>

        <div id="game-view">
            <div id="game-status" style="color:#4caf50; font-weight:bold; margin-top:10px;">🔴 TAPHA DEEMAA JIRU...</div>
            <div class="ball" id="ball-call">--</div>
            <div class="cards-grid" id="my-cards-ui"></div>
        </div>

        <script>
            let balance = localStorage.getItem('bingo_v15_bal') ? parseFloat(localStorage.getItem('bingo_v15_bal')) : 500.00;
            function updateUI() { document.getElementById('bal-text').innerText = balance.toFixed(2); localStorage.setItem('bingo_v15_bal', balance); }
            updateUI();

            let myTickets = [], allCards = [], isPlayingThisRound = false, isDone = false;

            const grid = document.getElementById('grid-100');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div'); d.className = 't-num'; d.innerText = i;
                d.onclick = () => {
                    if(myTickets.includes(i)) { myTickets = myTickets.filter(t => t !== i); d.classList.remove('selected'); balance += 10; }
                    else if(myTickets.length < 10 && balance >= 10) { myTickets.push(i); d.classList.add('selected'); balance -= 10; }
                    updateUI();
                };
                grid.appendChild(d);
            }

            // 🕒 GLOBAL TIMER (Cycle is 60s)
            setInterval(() => {
                let now = Math.floor(Date.now() / 1000);
                let remaining = 60 - (now % 60);
                document.getElementById('sync-timer').innerText = remaining;

                if(remaining === 59) { // Cycle haaraa jalqabuu isaa
                    if(myTickets.length > 0) {
                        isPlayingThisRound = true;
                        startLiveGame();
                    } else {
                        isPlayingThisRound = false;
                        // Yoo tikeetii hin qabne taajjabdii qofa
                        document.getElementById('select-view').style.display = 'none';
                        document.getElementById('game-view').style.display = 'block';
                        document.getElementById('game-status').innerText = "👀 TAAJJABDII QOFA (Tikeetii hin qabdu)";
                        runBalls();
                    }
                }
            }, 1000);

            function startLiveGame() {
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                document.getElementById('game-status').innerText = "🔴 HIRMAACHAA JIRTA!";
                
                myTickets.forEach(id => {
                    let card = { id: id, nums: [], marks: new Array(25).fill(false) };
                    card.marks[12] = true;
                    let p = Array.from({length: 75}, (_, i) => i + 1);
                    for(let k=0; k<25; k++) card.nums.push(p.splice(Math.floor(Math.random()*p.length), 1)[0]);
                    
                    const div = document.createElement('div'); div.className = 'card active';
                    div.innerHTML = `<div class="b-grid" id="g-${id}"></div><div style="font-size:0.6rem; color:#4caf50;">#${id} ACTIVE</div>`;
                    document.getElementById('my-cards-ui').appendChild(div);
                    
                    card.nums.forEach((n, idx) => {
                        const c = document.createElement('div'); c.className = 'cell'; c.id = `c-${id}-${idx}`;
                        c.innerText = (idx === 12) ? "F" : n; if(idx === 12) c.classList.add('marked');
                        document.getElementById(`g-${id}`).appendChild(c);
                    });
                    allCards.push(card);
                });
                runBalls();
            }

            function runBalls() {
                let pool = Array.from({length: 75}, (_, i) => i + 1);
                const loop = setInterval(() => {
                    if(isDone || pool.length === 0) { clearInterval(loop); return; }
                    let picked = pool.splice(Math.floor(Math.random()*pool.length), 1)[0];
                    document.getElementById('ball-call').innerText = picked;

                    if(isPlayingThisRound) {
                        allCards.forEach(card => {
                            card.nums.forEach((n, idx) => {
                                if(n === picked) {
                                    card.marks[idx] = true;
                                    document.getElementById(`c-${card.id}-${idx}`).classList.add('marked');
                                }
                            });
                            if(checkBingo(card.marks)) {
                                isDone = true; balance += 700; updateUI();
                                document.getElementById('win-id').innerText = card.id;
                                document.getElementById('win-overlay').style.display = 'flex';
                            }
                        });
                    }
                }, 3000);
            }

            function checkBingo(m) {
                for(let i=0; i<5; i++) {
                    if(m[i*5] && m[i*5+1] && m[i*5+2] && m[i*5+3] && m[i*5+4]) return true;
                    if(m[i] && m[i+5] && m[i+10] && m[i+15] && m[i+20]) return true;
                }
                return false;
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
    time.sleep(2)
    try:
        bot.remove_webhook()
        bot.polling(none_stop=True)
    except:
        pass
