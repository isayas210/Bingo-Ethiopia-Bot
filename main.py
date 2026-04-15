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
        <title>Bingo Ethiopia 100 Cards</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { background-color: #0b0b0b; color: white; font-family: sans-serif; text-align: center; margin: 0; padding: 5px; }
            .nav { display: flex; justify-content: space-between; background: #0088cc; padding: 12px; border-radius: 0 0 15px 15px; font-weight: bold; position: sticky; top: 0; z-index: 100; }
            .wallet { background: #000; padding: 2px 10px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; }
            
            #timer { font-size: 24px; color: #ffeb3b; margin: 10px; }
            
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 8px; background: #1a1a1a; border-radius: 10px; }
            .t-num { aspect-ratio: 1; background: #333; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 3px; font-weight: bold; }
            .t-num.selected { background: #4caf50 !important; border: 1px solid white; }
            .t-num.taken { background: #ffeb3b !important; color: #000; }

            #game-view { display: none; }
            .ball { font-size: 35px; color: #ffeb3b; border: 4px solid #0088cc; border-radius: 50%; width: 90px; height: 90px; margin: 15px auto; display: flex; align-items: center; justify-content: center; background: #000; box-shadow: 0 0 15px #0088cc; }
            
            .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 5px; }
            .card { background: #151515; border: 1px solid #333; border-radius: 10px; padding: 5px; }
            .bingo-header { display: flex; justify-content: space-around; color: #0088cc; font-weight: 900; font-size: 1rem; border-bottom: 1px solid #222; margin-bottom: 4px; }
            
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #2a2a2a; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; border-radius: 2px; }
            .cell.marked { background: #4caf50 !important; animation: pop 0.3s ease; }
            
            #win-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
            @keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
        </style>
    </head>
    <body>
        <div id="win-overlay">
            <div style="background: #1a1a1a; padding: 30px; border-radius: 20px; border: 2px solid #ffeb3b; width: 80%;">
                <h1 style="color:#ffeb3b;">BINGO! 🏆</h1>
                <p>Kaarteellaa #<span id="win-id">--</span></p>
                <h2 style="color:#4caf50;">💰 +<span id="win-cash">700.00</span> ETB</h2>
                <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:12px 30px; border-radius:10px; font-weight:bold;">Tapha Haaraa</button>
            </div>
        </div>

        <div class="nav">
            <span>BINGO ETHIOPIA</span>
            <div class="wallet">💰 <span id="bal">500.00</span></div>
        </div>

        <div id="select-view">
            <div id="timer">⏰ <span id="time">40</span>s</div>
            <div class="selection-grid" id="s-grid"></div>
        </div>

        <div id="game-view">
            <div class="ball" id="call">--</div>
            <div class="cards-grid" id="c-grid"></div>
        </div>

        <script>
            let balance = 500.00;
            let myTickets = [];
            let others = [5, 12, 24, 56, 88]; // Kelloo ta'uuf
            let pool = 1000; // Tikeetii 100 x 10 ETB
            let isOver = false;

            const grid = document.getElementById('s-grid');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div');
                d.className = 't-num';
                d.innerText = i;
                if(others.includes(i)) d.classList.add('taken');
                else {
                    d.onclick = () => {
                        if(myTickets.length < 8 || d.classList.contains('selected')) {
                            if(!d.classList.contains('selected') && balance >= 10) {
                                d.classList.add('selected'); myTickets.push(i); balance -= 10;
                            } else if(d.classList.contains('selected')) {
                                d.classList.remove('selected'); myTickets = myTickets.filter(x => x !== i); balance += 10;
                            }
                            document.getElementById('bal').innerText = balance.toFixed(2);
                        }
                    };
                }
                grid.appendChild(d);
            }

            let sec = 40;
            const cd = setInterval(() => {
                sec--; document.getElementById('time').innerText = sec;
                if(sec <= 0) { clearInterval(cd); start(); }
            }, 1000);

            function start() {
                document.getElementById('select-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                
                // Namichaaf kan inni kute qofa mul'isuuf (Tikeetii 100nuu keessaa)
                myTickets.forEach(id => {
                    const w = document.createElement('div'); w.className = 'card';
                    w.innerHTML = `<div class="bingo-header"><span>B</span><span>I</span><span>N</span><span>G</span><span>O</span></div><div style="font-size:0.6rem; color:#aaa;">#${id}</div>`;
                    const g = document.createElement('div'); g.className = 'b-grid'; g.id = `t-${id}`;
                    let nums = []; while(nums.length < 25) { let r = Math.floor(Math.random()*75)+1; if(!nums.includes(r)) nums.push(r); }
                    nums.forEach((n, idx) => {
                        const c = document.createElement('div'); c.className = 'cell';
                        c.dataset.val = (idx === 12) ? "FREE" : n; c.innerText = c.dataset.val;
                        if(idx === 12) c.classList.add('marked');
                        g.appendChild(c);
                    });
                    w.appendChild(g); document.getElementById('c-grid').appendChild(w);
                });
                play();
            }

            function play() {
                const L = ['B','I','N','G','O'];
                const loop = setInterval(() => {
                    if(isOver) { clearInterval(loop); return; }
                    let num = Math.floor(Math.random()*75)+1;
                    document.getElementById('call').innerText = L[Math.floor(Math.random()*5)] + " " + num;
                    document.querySelectorAll('.cell').forEach(c => {
                        if(c.dataset.val == num) { c.classList.add('marked'); check(c.parentElement); }
                    });
                }, 4000);
            }

            function check(g) {
                const cells = Array.from(g.children);
                const m = cells.map(c => c.classList.contains('marked'));
                let won = false;
                for(let i=0; i<5; i++) {
                    if(m[i*5] && m[i*5+1] && m[i*5+2] && m[i*5+3] && m[i*5+4]) won = true;
                    if(m[i] && m[i+5] && m[i+10] && m[i+15] && m[i+20]) won = true;
                }
                if(won && !isOver) {
                    isOver = true;
                    let prize = 700; // 1000 - 300 (%30) = 700
                    balance += prize;
                    document.getElementById('win-overlay').style.display = 'flex';
                    document.getElementById('win-id').innerText = g.id.replace('t-','');
                    document.getElementById('bal').innerText = balance.toFixed(2);
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
