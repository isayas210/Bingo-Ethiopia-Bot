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
        <title>Bingo Ethiopia - Pro Gaming</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #000; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 5px; overflow-x: hidden; }
            .header-nav { display: flex; justify-content: space-between; align-items: center; background: #0088cc; padding: 10px; border-radius: 10px; margin-bottom: 10px; position: sticky; top: 0; z-index: 100; }
            .balance-box { background: #000; padding: 5px 12px; border-radius: 20px; color: #4caf50; font-weight: bold; border: 1px solid #4caf50; }
            
            #timer-box { font-size: 20px; color: #ffeb3b; margin: 10px; font-weight: bold; }
            
            /* 1-100 Ticket Selection */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; background: #111; padding: 8px; border-radius: 10px; border: 1px solid #333; }
            .t-num { aspect-ratio: 1; background: #f44336; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 3px; font-weight: bold; cursor: pointer; }
            .t-num.selected { background: #4caf50 !important; }

            /* Game Layout */
            #game-area { display: none; }
            .call-circle { font-size: 28px; color: #ffeb3b; border: 3px dashed #0088cc; border-radius: 50%; width: 75px; height: 75px; margin: 10px auto; display: flex; align-items: center; justify-content: center; background: #111; box-shadow: 0 0 15px rgba(0,136,204,0.5); }
            
            .cards-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; padding: 5px; }
            .card-wrapper { background: #1a1a1a; border: 1px solid #444; border-radius: 8px; padding: 4px; }
            .card-title { font-size: 0.7rem; color: #0088cc; margin-bottom: 3px; font-weight: bold; }
            
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #333; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 2px; font-weight: bold; }
            .cell.marked { background: #4caf50 !important; color: white; animation: pop 0.3s ease; }
            
            @keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }

            #win-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
            .win-msg { font-size: 2rem; color: #ffeb3b; font-weight: bold; text-shadow: 0 0 10px #ff9800; }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <div class="win-msg">🎊 BINGO! 🎊</div>
            <p>Karteellaa #<span id="winning-ticket">--</span> Injifatteetta!</p>
            <button onclick="location.reload()" style="padding:15px 30px; background:#4caf50; border:none; color:white; border-radius:10px; font-weight:bold; margin-top:20px;">Tapha Haaraa</button>
        </div>

        <div class="header-nav">
            <span style="font-weight: bold;">BINGO 🇪🇹</span>
            <div class="balance-box">💰 <span id="balance">500.00</span> ETB</div>
        </div>

        <div id="selection-screen">
            <div id="timer-box">⏱ <span id="seconds">40</span>s</div>
            <p style="font-size: 0.8rem; margin: 5px;">Tikeetii Filadhu (Gatii: 5 ETB)</p>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div class="call-circle" id="call-display">--</div>
            <div class="cards-container" id="cards-grid"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let balance = 500.00;
            let timeLeft = 40;
            let selected = [];
            let gameEnded = false;

            // 1. Grid 1-100 Selection
            const box = document.getElementById('selection-box');
            for(let i=1; i<=100; i++) {
                const div = document.createElement('div');
                div.className = 't-num';
                div.innerText = i;
                div.onclick = function() {
                    if(selected.length < 8 || this.classList.contains('selected')) {
                        if(!this.classList.contains('selected')) {
                            if(balance >= 5) {
                                this.classList.add('selected');
                                selected.push(i);
                                balance -= 5.00;
                                updateBalance();
                            } else { alert("Balance kee gahaa miti!"); }
                        } else {
                            this.classList.remove('selected');
                            selected = selected.filter(n => n !== i);
                            balance += 5.00;
                            updateBalance();
                        }
                    }
                };
                box.appendChild(div);
            }

            function updateBalance() { document.getElementById('balance').innerText = balance.toFixed(2); }

            // 2. Timer
            const counter = setInterval(() => {
                timeLeft--;
                document.getElementById('seconds').innerText = timeLeft;
                if(timeLeft <= 0) {
                    clearInterval(counter);
                    if(selected.length > 0) startGame();
                    else location.reload();
                }
            }, 1000);

            // 3. Game Logic
            function startGame() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                const container = document.getElementById('cards-grid');

                selected.forEach(ticketId => {
                    const wrap = document.createElement('div');
                    wrap.className = 'card-wrapper';
                    wrap.innerHTML = `<div class="card-title">BINGO #${ticketId}</div>`;
                    const g = document.createElement('div');
                    g.className = 'bingo-grid';
                    g.id = `ticket-${ticketId}`;
                    
                    let nums = [];
                    while(nums.length < 25) {
                        let r = Math.floor(Math.random() * 75) + 1;
                        if(!nums.includes(r)) nums.push(r);
                    }

                    nums.forEach((n, i) => {
                        const cell = document.createElement('div');
                        cell.className = 'cell';
                        cell.dataset.val = (i === 12) ? "FREE" : n;
                        cell.innerText = cell.dataset.val;
                        if(i === 12) cell.classList.add('marked');
                        g.appendChild(cell);
                    });
                    wrap.appendChild(g);
                    container.appendChild(wrap);
                });
                startCallingLoop();
            }

            function startCallingLoop() {
                const letters = ['B', 'I', 'N', 'G', 'O'];
                const interval = setInterval(() => {
                    if(gameEnded) { clearInterval(interval); return; }
                    
                    let char = letters[Math.floor(Math.random()*5)];
                    let num = Math.floor(Math.random()*75)+1;
                    document.getElementById('call-display').innerText = char + " " + num;

                    document.querySelectorAll('.cell').forEach(cell => {
                        if(cell.dataset.val == num) {
                            cell.classList.add('marked');
                            checkWinningLine(cell.parentElement);
                        }
                    });
                }, 4000);
            }

            function checkWinningLine(grid) {
                const cells = Array.from(grid.children);
                const marked = cells.map(c => c.classList.contains('marked'));
                
                // Logic sarara 1 (Rows & Columns)
                let won = false;
                for(let i=0; i<5; i++) {
                    // Rows
                    if(marked[i*5] && marked[i*5+1] && marked[i*5+2] && marked[i*5+3] && marked[i*5+4]) won = true;
                    // Columns
                    if(marked[i] && marked[i+5] && marked[i+10] && marked[i+15] && marked[i+20]) won = true;
                }

                if(won && !gameEnded) {
                    gameEnded = true;
                    balance += 100.00; // Fake Winning Amount
                    updateBalance();
                    document.getElementById('win-overlay').style.display = 'flex';
                    document.getElementById('winning-ticket').innerText = grid.id.replace('ticket-','');
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
