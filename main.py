import telebot
from flask import Flask
import os
from threading import Thread

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
        <title>Bingo Ethiopia Mini App</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { 
                background-color: #000; color: white; font-family: sans-serif; 
                text-align: center; margin: 0; padding: 10px; overflow-x: hidden;
            }
            .header { background: #0088cc; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
            
            #timer-box { font-size: 20px; color: #ffeb3b; margin: 10px; font-weight: bold; }
            
            /* Selection Grid 1-100 */
            .selection-grid { 
                display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; 
                max-width: 100%; margin: 0 auto; background: #1a1a1a; padding: 8px; border-radius: 8px;
            }
            .t-num { 
                aspect-ratio: 1; background: #f44336; /* Diimaa: Bilisa */
                display: flex; align-items: center; justify-content: center; 
                font-size: 0.7rem; border-radius: 2px; cursor: pointer; font-weight: bold;
            }
            .t-num.selected { background: #4caf50 !important; } /* Magariisa: Ati filatte */
            .t-num.taken { background: #ffeb3b !important; color: #000; cursor: not-allowed; } /* Kelloo: Nama biraa */

            /* Game Area */
            #game-area { display: none; }
            .call-circle { 
                font-size: 28px; color: #ffeb3b; margin: 15px auto; 
                border: 3px solid #0088cc; border-radius: 50%; width: 70px; height: 70px;
                display: flex; align-items: center; justify-content: center;
            }
            .bingo-grid { 
                display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; 
                max-width: 320px; margin: 0 auto;
            }
            .cell { 
                background: #222; border: 1px solid #444; aspect-ratio: 1; 
                display: flex; align-items: center; justify-content: center; 
                border-radius: 5px; font-size: 1.1rem;
            }
            .cell.marked { background: #0088cc; color: white; }
        </style>
    </head>
    <body>
        <div id="selection-screen">
            <div class="header">Karteellaa Filadhu (1-100)</div>
            <div id="timer-box">⏰ <span id="seconds">40</span>s</div>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div class="header">Tapha Bingo</div>
            <div class="call-circle" id="call-display">--</div>
            <div class="bingo-grid" id="bingo-card"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand(); // Mini App guutummaatti akka banamu

            let timeLeft = 40;
            let selected = [];
            let taken = [2, 15, 44, 78]; // Fakkeenyaaf qabaman

            // 1. Grid 1-100 uumuu
            const box = document.getElementById('selection-box');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div');
                d.className = 't-num';
                d.innerText = i;
                if(taken.includes(i)) {
                    d.classList.add('taken');
                } else {
                    d.onclick = function() {
                        this.classList.toggle('selected');
                        if(this.classList.contains('selected')) selected.push(i);
                        else selected = selected.filter(n => n !== i);
                    };
                }
                box.appendChild(d);
            }

            // 2. Timer
            const counter = setInterval(() => {
                timeLeft--;
                document.getElementById('seconds').innerText = timeLeft;
                if(timeLeft <= 0) {
                    clearInterval(counter);
                    if(selected.length > 0) startBingo();
                    else { alert("Tikeetii hin filanne!"); location.reload(); }
                }
            }, 1000);

            // 3. Bingo Start
            function startBingo() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                
                const grid = document.getElementById('bingo-card');
                let nums = [];
                while(nums.length < 25) {
                    let r = Math.floor(Math.random() * 75) + 1;
                    if(!nums.includes(r)) nums.push(r);
                }

                nums.forEach((n, i) => {
                    const c = document.createElement('div');
                    c.className = 'cell';
                    c.innerText = (i === 12) ? "FREE" : n;
                    if(i === 12) c.classList.add('marked');
                    c.onclick = function() { this.classList.toggle('marked'); };
                    grid.appendChild(c);
                });

                const letters = ['B', 'I', 'N', 'G', 'O'];
                setInterval(() => {
                    let L = letters[Math.floor(Math.random()*5)];
                    let N = Math.floor(Math.random()*75)+1;
                    document.getElementById('call-display').innerText = L + "" + N;
                }, 4000);
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
