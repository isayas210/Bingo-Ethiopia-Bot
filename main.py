import telebot
from flask import Flask
import os
from threading import Thread
import time

# Token kee qofa as galchi
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
            body { background-color: #0b0b0b; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 5px; }
            .header-nav { display: flex; justify-content: space-between; background: #0088cc; padding: 12px; border-radius: 0 0 15px 15px; font-weight: bold; position: sticky; top: 0; z-index: 100; }
            .wallet { background: #000; padding: 3px 12px; border-radius: 20px; color: #4caf50; border: 1px solid #4caf50; font-size: 0.85rem; }
            
            #timer-box { font-size: 24px; color: #ffeb3b; margin: 10px; font-weight: 800; }
            
            /* 1-100 Selection Grid */
            .selection-grid { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; padding: 8px; background: #1a1a1a; border-radius: 10px; }
            .t-num { aspect-ratio: 1; background: #333; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 4px; font-weight: bold; border: 1px solid #444; }
            .t-num.selected { background: #4caf50 !important; border: 1px solid white; } /* Magariisa: Kan kee */
            .t-num.taken { background: #ffeb3b !important; color: #000; } /* Kelloo: Kan namni biraa dursee kute */

            /* Game Area */
            #game-area { display: none; }
            .ball-caller { font-size: 35px; color: #ffeb3b; border: 5px solid #0088cc; border-radius: 50%; width: 90px; height: 90px; margin: 20px auto; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #222, #000); box-shadow: 0 0 20px rgba(0,136,204,0.6); }
            
            .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 5px; }
            .card-box { background: #151515; border: 1px solid #333; border-radius: 12px; padding: 6px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            
            /* Bingo Header Logic */
            .bingo-header { display: grid; grid-template-columns: repeat(5, 1fr); color: #0088cc; font-weight: 900; font-size: 1rem; margin-bottom: 5px; border-bottom: 1px solid #222; }
            
            .b-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; }
            .cell { background: #2a2a2a; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; border-radius: 3px; font-weight: bold; color: #ddd; }
            .cell.marked { background: #4caf50 !important; color: white; animation: pop 0.4s ease; }
            
            @keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }

            /* Winner Modal */
            #win-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 1000; flex-direction: column; align-items: center; justify-content: center; }
            .win-content { background: #1a1a1a; padding: 30px; border-radius: 20px; border: 3px solid #ffeb3b; width: 85%; }
            .cash-text { font-size: 2rem; color: #4caf50; font-weight: bold; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div id="win-modal">
            <div class="win-content">
                <h1 style="color:#ffeb3b; margin:0;">BINGO! 🏆</h1>
                <p style="font-size:1.1rem;">Karteellaa #<span id="win-id">--</span></p>
                <div class="cash-text">💰 +<span id="win-amount">0</span> ETB</div>
                <p style="font-size:0.8rem; color:#aaa;">(Hirdhii %30 booda)</p>
                <button onclick="location.reload()" style="background:#0088cc; color:white; border:none; padding:15px 40px; border-radius:12px; font-weight:bold; font-size:1rem; cursor:pointer;">Tapha Haaraa</button>
            </div>
        </div>

        <div class="header-nav">
            <span>BINGO ETHIOPIA 🇪🇹</span>
            <div class="wallet">💰 <span id="balance">500.00</span></div>
        </div>

        <div id="select-page">
            <div id="timer-box">⏰ <span id="time-left">40</span>s</div>
            <p style="font-size:0.85rem; color:#888;">Kaarteellaa filadhu (10 ETB)</p>
            <div class="selection-grid" id="s-grid"></div>
        </div>

        <div id="game-area">
            <div class="ball-caller" id="call-display">--</div>
            <div class="cards-grid" id="c-grid"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let balance = 500.00;
            let myTickets = [];
            let othersTickets = [2, 18, 44, 76, 92]; // Kelloo ta'uuf fakkeenya
            let poolMoney = 0;
            let gameOver = false;

            const grid = document.getElementById('s-grid');
            for(let i=1; i<=100; i++) {
                const d = document.createElement('div');
                d.className = 't-num';
                d.innerText = i;
                if(othersTickets.includes(i)) {
                    d.classList.add('taken');
                } else {
                    d.onclick = () => {
                        if(myTickets.length < 8 || d.classList.contains('selected')) {
                            if(!d.classList.contains('selected') && balance >= 10) {
                                d.classList.add('selected'); myTickets.push(i); balance -= 10; poolMoney += 10;
                            } else if(d.classList.contains('selected')) {
                                d.classList.remove('selected'); myTickets = myTickets.filter(x => x !== i); balance += 10; poolMoney -= 10;
                            }
                            document.getElementById('balance').innerText = balance.toFixed(2);
                        }
                    };
                }
                grid.appendChild(d);
            }

            let sec = 40;
            const timer = setInterval(() => {
                sec--; document.getElementById('time-left').innerText = sec;
                if(sec <= 0) { clearInterval(timer); startBingo(); }
            }, 1000);

            function startBingo() {
                if(myTickets.length === 0) { location.reload(); return; }
                document.getElementById('select-page').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                
                myTickets.forEach(tid => {
                    const wrap = document.createElement('div'); wrap.className = 'card-box';
                    wrap.innerHTML = `
                        <div class="bingo-header"><span>B</span><span>I</span><span>N</span><span>G</span><span>O</span></div>
                        <div style="font-size:0.65rem; color:#0088cc; margin-bottom:4px;">CARD #${tid}</div>
                    `;
                    const g = document.createElement('div'); g.className = 'b-grid'; g.id = `ticket-${tid}`;
                    let nums = []; while(nums.length < 25) { let r = Math.floor(Math.random()*75)+1; if(!nums.includes(r)) nums.push(r); }
                    nums.forEach((n, idx) => {
                        const c = document.createElement('div'); c.className = 'cell';
                        c.dataset.val = (idx === 12) ? "FREE" : n; c.innerText = c.dataset.val;
                        if(idx === 12) c.classList.add('marked');
                        g.appendChild(c);
                    });
                    wrap.appendChild(g); document.getElementById('c-grid').appendChild(wrap);
                });
                runCallerLoop();
            }

            function runCallerLoop() {
                const letters = ['B','I','N','G','O'];
                const loop = setInterval(() => {
                    if(gameOver) { clearInterval(loop); return; }
                    let num = Math.floor(Math.random()*75)+1;
                    document.getElementById('call-display').innerText = letters[Math.floor(Math.random()*5)] + " " + num;
                    document.querySelectorAll('.cell').forEach(c => {
                        if(c.dataset.val == num) { c.classList.add('marked'); checkWin(c.parentElement); }
                    });
                }, 4000);
            }

            function checkWin(gridElement) {
                const cells = Array.from(gridElement.children);
                const marked = cells.map(c => c.classList.contains('marked'));
                let won = false;
                for(let i=0; i<5; i++) {
                    // Row Check
                    if(marked[i*5] && marked[i*5+1] && marked[i*5+2] && marked[i*5+3] && marked[i*5+4]) won = true;
                    // Column Check
                    if(marked[i] && marked[i+5] && marked[i+10] && marked[i+15] && marked[i+20]) won = true;
                }
                if(won && !gameOver) {
                    gameOver = true;
                    let prize = poolMoney * 0.7; // %30 commission
                    balance += prize;
                    document.getElementById('win-modal').style.display = 'flex';
                    document.getElementById('win-id').innerText = gridElement.id.replace('ticket-','');
                    document.getElementById('win-amount').innerText = prize.toFixed(2);
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
    print("Conflict removed. Starting bot...")
    bot.polling(none_stop=True)
