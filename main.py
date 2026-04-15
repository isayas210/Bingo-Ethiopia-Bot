import telebot
from flask import Flask
import os
from threading import Thread

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
        <title>Bingo Ethiopia - Multi-Card</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #000; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .header { background: #0088cc; padding: 10px; border-radius: 10px; font-weight: bold; margin-bottom: 5px; }
            #timer-box { font-size: 18px; color: #ffeb3b; margin: 5px; }
            
            /* Selection Grid 1-100 */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; padding: 5px; background: #111; border-radius: 8px; }
            .t-num { aspect-ratio: 1; background: #f44336; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 2px; cursor: pointer; }
            .t-num.selected { background: #4caf50 !important; }
            .t-num.taken { background: #ffeb3b !important; color: #000; }

            /* Game Layout */
            #game-area { display: none; }
            .call-box { font-size: 28px; color: #ffeb3b; border: 2px dashed #0088cc; border-radius: 15px; width: 100px; margin: 10px auto; padding: 10px; }
            
            /* Multi-Card Grid: 1 fuula irratti 8 akka mul'atuuf */
            .cards-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 5px; }
            .card-wrapper { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 5px; }
            .card-title { font-size: 0.8rem; color: #0088cc; margin-bottom: 3px; font-weight: bold; }
            
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #333; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; border-radius: 2px; }
            .cell.marked { background: #4caf50 !important; color: white; } /* Ofumaan Magariisa ta'a */
            
            #winner-notif { display: none; background: #ff9800; color: black; padding: 10px; border-radius: 10px; font-weight: bold; margin: 10px; }
        </style>
    </head>
    <body>
        <div id="selection-screen">
            <div class="header">Karteellaa Filadhu (Hanga 8)</div>
            <div id="timer-box">⏱ <span id="seconds">40</span>s</div>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div id="winner-notif">🎊 INJIFATAA: Karteellaa #<span id="winner-num">--</span>!</div>
            <div class="call-box" id="call-display">--</div>
            <div class="cards-container" id="all-cards"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let timeLeft = 40;
            let selectedCards = [];
            let calledNumbers = new Set();

            // 1. Grid 1-100
            const selectionBox = document.getElementById('selection-box');
            for(let i=1; i<=100; i++) {
                const div = document.createElement('div');
                div.className = 't-num';
                div.innerText = i;
                div.onclick = function() {
                    if(selectedCards.length < 8 || this.classList.contains('selected')) {
                        this.classList.toggle('selected');
                        if(this.classList.contains('selected')) selectedCards.push(i);
                        else selectedCards = selectedCards.filter(n => n !== i);
                    }
                };
                selectionBox.appendChild(div);
            }

            // 2. Timer
            const timer = setInterval(() => {
                timeLeft--;
                document.getElementById('seconds').innerText = timeLeft;
                if(timeLeft <= 0) {
                    clearInterval(timer);
                    if(selectedCards.length > 0) startGame();
                    else location.reload();
                }
            }, 1000);

            // 3. Start Game
            function startGame() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                const container = document.getElementById('all-cards');

                selectedCards.forEach(cardNum => {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'card-wrapper';
                    wrapper.innerHTML = `<div class="card-title">BINGO #${cardNum}</div>`;
                    
                    const grid = document.createElement('div');
                    grid.className = 'bingo-grid';
                    grid.id = `card-${cardNum}`;
                    
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
                        grid.appendChild(cell);
                    });
                    wrapper.appendChild(grid);
                    container.appendChild(wrapper);
                });

                startCalling();
            }

            // 4. Calling & Auto-Marking
            function startCalling() {
                const letters = ['B', 'I', 'N', 'G', 'O'];
                const interval = setInterval(() => {
                    let L = letters[Math.floor(Math.random()*5)];
                    let N = Math.floor(Math.random()*75)+1;
                    let fullCall = L + " " + N;
                    document.getElementById('call-display').innerText = fullCall;
                    calledNumbers.add(N);

                    // Ofumaan mallattoo magariisa gochuu (Auto-mark)
                    document.querySelectorAll('.cell').forEach(cell => {
                        if(cell.dataset.val == N) {
                            cell.classList.add('marked');
                            checkBingo(cell.parentElement);
                        }
                    });
                }, 4000);
            }

            function checkBingo(grid) {
                // Hojiin injifataa beeksisuu asitti dabalama
                // Fakkeenyaaf yoo sararri tokko guute:
                document.getElementById('winner-notif').style.display = 'block';
                document.getElementById('winner-num').innerText = grid.id.replace('card-', '');
            }
        </script>
    </body>
    </html>
    """

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.remove_webhook()
    bot.polling(none_stop=True)
