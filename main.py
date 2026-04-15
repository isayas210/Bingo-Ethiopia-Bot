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
        <title>Bingo Ethiopia</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #0b0b0b; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .nav { display: flex; justify-content: space-between; background: #0088cc; padding: 12px; border-radius: 0 0 15px 15px; font-weight: bold; position: sticky; top: 0; z-index: 100; }
            .wallet { background: #000; padding: 2px 12px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; }
            #timer { font-size: 26px; color: #ffeb3b; margin: 15px; font-weight: bold; }
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 10px; background: #1a1a1a; border-radius: 12px; }
            .t-num { aspect-ratio: 1; background: #333; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 4px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; border: 1px solid white; }
            #game-view { display: none; }
            .ball { font-size: 38px; color: #ffeb3b; border: 5px solid #0088cc; border-radius: 50%; width: 95px; height: 95px; margin: 20px auto; display: flex; align-items: center; justify-content: center; background: #000; box-shadow: 0 0 20px rgba(0,136,204,0.5); }
            .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 5px; }
            .card { background: #151515; border: 1px solid #333; border-radius: 12px; padding: 8px; }
            .bingo-header { display: flex; justify-content: space-around; color: #0088cc; font-weight: 900; font-size: 1.1rem; border-bottom: 1px solid #222; margin-bottom: 5px; }
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; }
            .cell { background: #262626; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 3px; }
            .cell.marked { background: #4caf50 !important; }
            #win-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
            #house-msg { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a1a; padding: 25px; border-radius: 20px; border: 2px solid #ffeb3b; display: none; z-index: 2000; width: 80%; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <div style="background: #1a1a1a; padding: 35px; border-radius: 25px; border: 2px solid #ffeb3b; width: 85%;">
                <h1 style="color:#ffeb3b;">BINGO! 🏆</h1>
                <p>Kaarteellaa #<span id="win-id">--</span> mo'ateera!</p>
                <h2 style="color:#4caf50; font-size: 2rem;">💰 +700.00 ETB</h2>
                <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:12px 30px; border-radius:12px; font-weight:bold;">Tapha Haaraa</button>
            </div>
        </div>

        <div id="house-msg">
            <h2 style="color: #ffeb3b;">GAME OVER</h2>
            <p>Kaarteellaa #<span id="toast-id"></span> Bingo!</p>
            <p style="font-size: 0.8rem; color: #888;">Tapha itti aanuuf tikeetii kutadhu.</p>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA 🇪🇹</span>
            <div class="wallet">💰 <span id="bal-text">---</span></div>
        </div>

        <div id="select-view">
            <div id="timer">⏰ <span id="sec">40</span>s</div>
            <div class="selection-grid" id="grid-100"></div>
        </div>

        <div id="game-view">
            <div class="ball" id="ball-call">--</div>
            <div class="cards-grid" id="my-cards"></div>
        </div>

        <script>
            let balance = localStorage.getItem('bingo_persist_bal') ? parseFloat(localStorage.getItem('bingo_persist_bal')) : 500.00;
            function updateUI() { document.getElementById('bal-text').innerText = balance.toFixed(2); localStorage.setItem('bingo_persist_bal', balance); }
            updateUI();

            let myTickets = [], allCards = [], isDone = false;

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

            let timeLeft = 40;
            const timer = setInterval(() => { timeLeft--; document.getElementById('sec').innerText = timeLeft; if(timeLeft <= 0) { clearInterval(timer); start(); } }, 1000);

            function start() {
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                for(let id=1; id<=100; id++) {
                    let card = { id: id, isMine: myTickets.includes(id), nums: [], marks: new Array(25).fill(false), win: false };
                    card.marks[12] = true;
                    let p = Array.from({length: 75}, (_, i) => i + 1);
                    for(let k=0; k<25; k++) card.nums.push(p.splice(Math.floor(Math.random()*p.length), 1)[0]);
                    allCards.push(card);
                    if(card.isMine) {
                        const div = document.createElement('div'); div.className = 'card';
                        div.innerHTML = `<div class="bingo-header"><span>B</span><span>I</span><span>N</span><span>G</span><span>O</span></div><div class="b-grid" id="g-${id}"></div>`;
                        document.getElementById('my-cards').appendChild(div);
                        card.nums.forEach((n, idx) => {
                            const c = document.createElement('div'); c.className = 'cell'; c.id = `c-${id}-${idx}`;
                            c.innerText = (idx === 12) ? "F" : n; if(idx === 12) c.classList.add('marked');
                            document.getElementById(`g-${id}`).appendChild(c);
                        });
                    }
                }
                play();
            }

            function play() {
                let pool = Array.from({length: 75}, (_, i) => i + 1);
                const loop = setInterval(() => {
                    if(isDone || pool.length === 0) { clearInterval(loop); return; }
                    let picked = pool.splice(Math.floor(Math.random()*pool.length), 1)[0];
                    document.getElementById('ball-call').innerText = picked;
                    allCards.forEach(card => {
                        if(card.win) return;
                        card.nums.forEach((n, idx) => { if(n === picked) { card.marks[idx] = true; if(card.isMine) document.getElementById(`c-${card.id}-${idx}`).classList.add('marked'); } });
                        if(check(card.marks)) {
                            card.win = true; isDone = true;
                            if(card.isMine) {
                                balance += 700; updateUI();
                                document.getElementById('win-id').innerText = card.id;
                                document.getElementById('win-overlay').style.display = 'flex';
                            } else {
                                // HOUSE WIN RESET
                                document.getElementById('toast-id').innerText = card.id;
                                document.getElementById('house-msg').style.display = 'block';
                                setTimeout(() => { location.reload(); }, 3000);
                            }
                        }
                    });
                }, 3000);
            }

            function check(m) {
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
