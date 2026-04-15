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
        <title>Bingo Ethiopia - Royal Casino</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #0b0b0b; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 5px; }
            .header { display: flex; justify-content: space-between; background: #0088cc; padding: 12px; border-radius: 0 0 15px 15px; font-weight: bold; }
            .stat { background: #000; padding: 3px 10px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; font-size: 0.8rem; }
            
            #timer-box { font-size: 22px; color: #ffeb3b; margin: 10px; text-shadow: 0 0 5px #000; }
            
            /* Selection Grid 1-100 */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; background: #1a1a1a; padding: 8px; border-radius: 10px; }
            .t-num { aspect-ratio: 1; background: #f44336; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 3px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; } /* Magariisa: Kan kee */
            .t-num.taken { background: #ffeb3b !important; color: #000; } /* Kelloo: Kan biraa */

            /* Game Area */
            #game-area { display: none; }
            .caller-box { background: radial-gradient(circle, #222, #000); border: 3px solid #0088cc; border-radius: 50%; width: 85px; height: 85px; margin: 15px auto; display: flex; align-items: center; justify-content: center; font-size: 32px; color: #ffeb3b; font-weight: bold; }
            
            .cards-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 5px; }
            .card-wrapper { background: #151515; border: 1px solid #333; border-radius: 10px; padding: 5px; position: relative; }
            .card-header { display: flex; justify-content: space-around; font-weight: 900; color: #0088cc; font-size: 0.9rem; margin-bottom: 2px; border-bottom: 1px solid #222; }
            
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #2a2a2a; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 2px; font-weight: bold; }
            .cell.marked { background: #4caf50 !important; color: white; animation: pop 0.4s ease; }

            /* Win Overlay */
            #win-screen { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
            .win-box { background: #1a1a1a; padding: 25px; border-radius: 20px; border: 2px solid #ffeb3b; width: 80%; }
            .win-amount { font-size: 1.8rem; color: #4caf50; margin: 10px 0; font-weight: bold; }
            
            @keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
        </style>
    </head>
    <body>
        <div id="win-screen">
            <div class="win-box">
                <h1 style="color:#ffeb3b; margin:0;">BINGO! 🏆</h1>
                <p>Kaarteellaa #<span id="win-ticket-id">--</span></p>
                <div class="win-amount">💰 +<span id="win-prize">0</span> ETB</div>
                <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:12px 25px; border-radius:10px; font-weight:bold;">Tapha Haaraa</button>
            </div>
        </div>

        <div class="header">
            <span>BINGO 🇪🇹</span>
            <div class="stat">💰 <span id="balance">500.00</span></div>
        </div>

        <div id="selection-screen">
            <div id="timer-box">⏰ <span id="sec">40</span>s</div>
            <p style="font-size:0.8rem; color:#aaa;">Tikeetii filadhu (Gatii: 10 ETB)</p>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div class="caller-box" id="call-num">--</div>
            <div class="cards-container" id="cards-grid"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let bal = 500.00;
            let timeRemaining = 40;
            let mySelection = [];
            let takenByOthers = [5, 12, 45, 67, 88]; // Kelloo akka ta'uuf
            let pool = 0;
            let gameStarted = false;

            // 1. Grid 1-100
            const sBox = document.getElementById('selection-box');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div');
                d.className = 't-num';
                d.innerText = i;
                if(takenByOthers.includes(i)) {
                    d.classList.add('taken');
                } else {
                    d.onclick = function() {
                        if(mySelection.length < 8 || this.classList.contains('selected')) {
                            if(!this.classList.contains('selected')) {
                                if(bal >= 10) {
                                    this.classList.add('selected');
                                    mySelection.push(i);
                                    bal -= 10;
                                    pool += 10;
                                    updateUI();
                                }
                            } else {
                                this.classList.remove('selected');
                                mySelection = mySelection.filter(n => n !== i);
                                bal += 10;
                                pool -= 10;
                                updateUI();
                            }
                        }
                    };
                }
                sBox.appendChild(d);
            }

            function updateUI() { document.getElementById('balance').innerText = bal.toFixed(2); }

            const timer = setInterval(() => {
                timeRemaining--;
                document.getElementById('sec').innerText = timeRemaining;
                if(timeRemaining <= 0) {
                    clearInterval(timer);
                    startBingo();
                }
            }, 1000);

            function startBingo() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                const grid = document.getElementById('cards-grid');

                // Dirqama tikeetii 100 ni uuma (Kan namni hin kutanne "Mana" ta'a)
                for(let i=1; i<=100; i++) {
                    // Namichaaf kan inni kute qofa mul'isa (max 8)
                    if(mySelection.includes(i)) {
                        const wrap = document.createElement('div');
                        wrap.className = 'card-wrapper';
                        wrap.innerHTML = `
                            <div class="card-header"><span>B</span><span>I</span><span>N</span><span>G</span><span>O</span></div>
                            <div class="card-title" style="font-size:0.6rem; color:#4caf50;">#${i} (USER)</div>
                        `;
                        const g = document.createElement('div');
                        g.className = 'bingo-grid';
                        g.id = `ticket-${i}`;
                        
                        let nums = generateBingoNums();
                        nums.forEach((n, idx) => {
                            const c = document.createElement('div');
                            c.className = 'cell';
                            c.dataset.val = (idx === 12) ? "FREE" : n;
                            c.innerText = c.dataset.val;
                            if(idx === 12) c.classList.add('marked');
                            g.appendChild(c);
                        });
                        wrap.appendChild(g);
                        grid.appendChild(wrap);
                    }
                }
                beginCalling();
            }

            function generateBingoNums() {
                let n = [];
                while(n.length < 25) {
                    let r = Math.floor(Math.random() * 75) + 1;
                    if(!n.includes(r)) n.push(r);
                }
                return n;
            }

            function beginCalling() {
                const letters = ['B', 'I', 'N', 'G', 'O'];
                const callInt = setInterval(() => {
                    if(gameStarted) { clearInterval(callInt); return; }
                    let L = letters[Math.floor(Math.random()*5)];
                    let N = Math.floor(Math.random()*75)+1;
                    document.getElementById('call-num').innerText = L + " " + N;

                    document.querySelectorAll('.cell').forEach(cell => {
                        if(cell.dataset.val == N) {
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
                    if(m[i*5] && m[i*5+1] && m[i*5+2] && m[i*5+3] && m[i*5+4]) won = true;
                    if(m[i] && m[i+5] && m[i+10] && m[i+15] && m[i+20]) won = true;
                }

                if(won && !gameStarted) {
                    gameStarted = true;
                    let prize = (pool * 0.7); // %30 hir'ifamee %70 herregaatti
                    bal += prize;
                    updateUI();
                    document.getElementById('win-screen').style.display = 'flex';
                    document.getElementById('win-ticket-id').innerText = grid.id.replace('ticket-','');
                    document.getElementById('win-prize').innerText = prize.toFixed(2);
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
    bot.remove_webhook()
    bot.polling(none_stop=True)
