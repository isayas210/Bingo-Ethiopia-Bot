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
        <title>Bingo Ethiopia Pro</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #000; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .header { background: #0088cc; padding: 8px; border-radius: 10px; font-weight: bold; margin-bottom: 5px; font-size: 1.2rem; }
            #timer-box { font-size: 18px; color: #ffeb3b; margin: 5px; font-weight: bold; }
            
            /* 1-100 Grid */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; padding: 5px; background: #111; border-radius: 8px; border: 1px solid #333; }
            .t-num { aspect-ratio: 1; background: #f44336; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 2px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; }
            
            /* Game Layout */
            #game-area { display: none; }
            .call-container { background: #222; border-radius: 15px; padding: 10px; margin: 10px auto; width: fit-content; border: 2px solid #0088cc; }
            .call-text { font-size: 30px; color: #ffeb3b; font-weight: bold; letter-spacing: 2px; }
            
            /* Multi-Card (Up to 8) */
            .cards-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; padding: 5px; }
            .card-wrapper { background: #1a1a1a; border: 1px solid #444; border-radius: 8px; padding: 5px; box-shadow: 0 0 5px rgba(0,136,204,0.3); }
            .card-title { font-size: 0.75rem; color: #0088cc; margin-bottom: 4px; font-weight: bold; border-bottom: 1px solid #333; }
            
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #333; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 2px; font-weight: 600; }
            .cell.marked { background: #4caf50 !important; color: white; transform: scale(1.05); transition: 0.3s; }
            
            #winner-banner { display: none; background: linear-gradient(to right, #ff9800, #ff5722); color: white; padding: 12px; border-radius: 10px; font-weight: bold; margin: 10px; animation: blink 1s infinite; }
            @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <div id="selection-screen">
            <div class="header">BINGO ETHIOPIA 🇪🇹</div>
            <div id="timer-box">⏱ Yeroo Hafe: <span id="seconds">40</span>s</div>
            <p style="font-size: 0.8rem; color: #aaa;">Karteellaa hanga 8 filadhu</p>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div id="winner-banner">🏆 BINGO! Karteellaa #<span id="winner-id">--</span></div>
            <div class="call-container">
                <div class="call-text" id="call-display">-- --</div>
            </div>
            <div class="cards-container" id="cards-grid"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let timeLeft = 40;
            let selected = [];
            const box = document.getElementById('selection-box');

            for(let i=1; i<=100; i++) {
                const div = document.createElement('div');
                div.className = 't-num';
                div.innerText = i;
                div.onclick = function() {
                    if(selected.length < 8 || this.classList.contains('selected')) {
                        this.classList.toggle('selected');
                        if(this.classList.contains('selected')) selected.push(i);
                        else selected = selected.filter(n => n !== i);
                    }
                };
                box.appendChild(div);
            }

            const counter = setInterval(() => {
                timeLeft--;
                document.getElementById('seconds').innerText = timeLeft;
                if(timeLeft <= 0) {
                    clearInterval(counter);
                    if(selected.length > 0) startApp();
                    else location.reload();
                }
            }, 1000);

            function startApp() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                const container = document.getElementById('cards-grid');

                selected.forEach(id => {
                    const wrap = document.createElement('div');
                    wrap.className = 'card-wrapper';
                    wrap.innerHTML = `<div class="card-title">BINGO #${id}</div>`;
                    const g = document.createElement('div');
                    g.className = 'bingo-grid';
                    g.id = `card-${id}`;
                    
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
                beginCalling();
            }

            function beginCalling() {
                const L = ['B', 'I', 'N', 'G', 'O'];
                setInterval(() => {
                    let char = L[Math.floor(Math.random()*5)];
                    let num = Math.floor(Math.random()*75)+1;
                    document.getElementById('call-display').innerText = char + " " + num;

                    document.querySelectorAll('.cell').forEach(c => {
                        if(c.dataset.val == num) {
                            c.classList.add('marked');
                            checkWinner(c.parentElement);
                        }
                    });
                }, 4000);
            }

            function checkWinner(grid) {
                // Sarara (Row/Column) qorachuu asitti dabalama
                // Fakkeenyaaf yoo 15 mallatteeffame
                if(grid.querySelectorAll('.marked').length >= 15) {
                    document.getElementById('winner-banner').style.display = 'block';
                    document.getElementById('winner-id').innerText = grid.id.replace('card-','');
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
    # Conflict akka hin uumamneef
    time.sleep(2)
    bot.remove_webhook()
    print("Bot dammaqeera...")
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        time.sleep(5)
