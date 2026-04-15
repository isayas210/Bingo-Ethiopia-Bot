import telebot
from flask import Flask
import os
from threading import Thread

# Token kee isa sirrii
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia - Multiplayer</title>
        <style>
            body { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 10px; }
            .header { background: #0088cc; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
            
            #timer-box { font-size: 22px; color: #ffeb3b; margin: 15px; font-weight: bold; background: #333; padding: 10px; border-radius: 50px; display: inline-block; min-width: 150px; }
            
            /* Selection Grid 1-100 */
            .selection-grid { 
                display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; 
                max-width: 400px; margin: 0 auto; background: #222; padding: 10px; border-radius: 10px;
                border: 2px solid #444;
            }
            .t-num { 
                aspect-ratio: 1; background: #f44336; /* Diimaa: Bilisa */
                display: flex; align-items: center; justify-content: center; 
                font-size: 0.75rem; border-radius: 4px; cursor: pointer; font-weight: bold;
            }
            .t-num.selected { background: #4caf50 !important; color: white; } /* Magariisa: Ati filatte */
            .t-num.taken { background: #ffeb3b !important; color: black; cursor: not-allowed; } /* Kelloo: Nama biraa */

            /* Bingo Card & Calling Area */
            #game-area { display: none; margin-top: 20px; }
            .called-num-box { font-size: 30px; color: #ffeb3b; margin-bottom: 20px; padding: 20px; border: 3px dashed #0088cc; border-radius: 15px; display: inline-block; min-width: 120px; }
            
            .bingo-grid { 
                display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; 
                max-width: 320px; margin: 0 auto; background: #333; padding: 15px; border-radius: 10px;
            }
            .cell { background: #444; border: 1px solid #666; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 1.2rem; font-weight: bold; }
            .cell.marked { background: #0088cc; color: white; }
        </style>
    </head>
    <body>
        <div id="selection-screen">
            <div class="header"><h3>Filannoo Karteellaa (1-100)</h3></div>
            <div id="timer-box">⏱ Hafe: <span id="seconds">40</span>s</div>
            <p style="font-size: 0.9rem;">Karteellaa hanga feete filadhu:</p>
            <div class="selection-grid" id="selection-box"></div>
        </div>

        <div id="game-area">
            <div class="header"><h3>Tapha Bingo 🇪🇹</h3></div>
            <div class="called-num-box" id="call-display">Eegi...</div>
            <div class="bingo-grid" id="bingo-card-grid"></div>
            <p>Karteellaa kee jalaa lakkofsa waamame hordofi.</p>
        </div>

        <script>
            let timeLeft = 40;
            let selectedTickets = [];
            // Fakkeenyaaf lakk. qabaman (Database malee)
            let takenTickets = [7, 21, 54, 99]; 

            const selectionBox = document.getElementById('selection-box');
            
            // 1. Grid 1-100 uumuu
            for(let i=1; i<=100; i++) {
                const div = document.createElement('div');
                div.className = 't-num';
                div.innerText = i;
                
                if(takenTickets.includes(i)) {
                    div.classList.add('taken');
                } else {
                    div.onclick = function() {
                        this.classList.toggle('selected');
                        if(this.classList.contains('selected')) {
                            selectedTickets.push(i);
                        } else {
                            selectedTickets = selectedTickets.filter(n => n !== i);
                        }
                    };
                }
                selectionBox.appendChild(div);
            }

            // 2. Timer (40s)
            const timer = setInterval(() => {
                timeLeft--;
                document.getElementById('seconds').innerText = timeLeft;
                if(timeLeft <= 0) {
                    clearInterval(timer);
                    if(selectedTickets.length > 0) {
                        startGame();
                    } else {
                        alert("Yeroon xumurame! Karteellaa hin filanne.");
                        location.reload();
                    }
                }
            }, 1000);

            // 3. Tapha Jalqabuu
            function startGame() {
                document.getElementById('selection-screen').style.display = 'none';
                document.getElementById('game-area').style.display = 'block';
                
                const grid = document.getElementById('bingo-card-grid');
                let cardNums = [];
                while(cardNums.length < 25) {
                    let r = Math.floor(Math.random() * 75) + 1;
                    if(!cardNums.includes(r)) cardNums.push(r);
                }

                cardNums.forEach((num, index) => {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.innerText = (index === 12) ? "FREE" : num;
                    if(index === 12) cell.classList.add('marked');
                    cell.onclick = function() { this.classList.toggle('marked'); };
                    grid.appendChild(cell);
                });

                startBingoCalling();
            }

            // 4. Waamicha Lakkoofsaa (B 12, N 45...)
            function startBingoCalling() {
                const letters = ['B', 'I', 'N', 'G', 'O'];
                const display = document.getElementById('call-display');
                
                setInterval(() => {
                    let L = letters[Math.floor(Math.random() * 5)];
                    let N = Math.floor(Math.random() * 75) + 1;
                    display.innerText = L + " " + N;
                }, 5000); // Sekondii 5 hundaatti waama
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
