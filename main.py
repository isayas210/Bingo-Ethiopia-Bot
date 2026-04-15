import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia - Traditional Card</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 20px #00d4ff; }
            
            /* Selection Grid */
            .grid-100 { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 8px; border: 1px solid #333; }
            .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 4px; font-size: 10px; cursor: pointer; }
            .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; }

            /* Bingo Table UI */
            .bingo-card { width: 100%; border-collapse: collapse; margin-top: 20px; background: #000; border: 3px solid #ffcc00; border-radius: 10px; overflow: hidden; }
            .bingo-card th { background: #ffcc00; color: #000; padding: 10px 0; font-size: 20px; border-bottom: 2px solid #ffcc00; }
            .bingo-card td { border: 1px solid #333; height: 50px; width: 20%; font-size: 16px; font-weight: bold; background: #1a2a44; }
            .bingo-card td.marked { background: #28a745; color: white; box-shadow: inset 0 0 10px #fff; transition: 0.5s; }

            .ball-zone { margin: 20px 0; }
            .ball { font-size: 55px; font-weight: bold; background: white; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; border: 6px solid #ffcc00; display: inline-block; box-shadow: 0 0 20px #ffcc00; }
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; border: 3px solid #fff; margin-bottom: 15px; animation: pulse 1s infinite; }
            @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
            .timer { font-size: 22px; color: #ff4444; font-weight: bold; margin-bottom: 10px; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA</h2>
        
        <div id="selection-stage">
            <div class="timer">Hafe: <span id="time-left">40</span>s</div>
            <p style="font-size:13px; color:#00ffcc;">Qubee B-I-N-G-O jalatti lakkofsa 5-5 (25) filadhu:</p>
            <div class="grid-100" id="picker"></div>
            <p id="stat" style="margin-top:10px;">Filatame: 0/25</p>
            <button onclick="confirmStart()" style="background:#28a745; color:white; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">TIKEETII KUTI</button>
        </div>

        <div id="game-stage" style="display:none;">
            <div class="ball-zone"><div class="ball" id="currentBall">?</div></div>
            <div class="win-msg" id="winAlert">
                <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
                <p>SARARRI GUUTAMEERA!</p>
            </div>
            
            <table class="bingo-card">
                <thead>
                    <tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr>
                </thead>
                <tbody id="bingo-body">
                    </tbody>
            </table>
            <div id="logs" style="font-size:12px; color:#aaa; margin-top:15px; text-align:left;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let count = 40;
        let selected = [];
        let called = [];
        let isOver = false;

        // Picker 1-100
        const picker = document.getElementById('picker');
        for(let i=1; i<=100; i++) {
            let b = document.createElement('button');
            b.className = 'n-btn'; b.innerText = i;
            b.onclick = () => {
                if(selected.includes(i)) {
                    selected = selected.filter(x => x !== i); b.classList.remove('active');
                } else if(selected.length < 25) {
                    selected.push(i); b.classList.add('active');
                }
                document.getElementById('stat').innerText = "Filatame: " + selected.length + "/25";
            };
            picker.appendChild(b);
        }

        let timerId = setInterval(() => {
            count--; document.getElementById('time-left').innerText = count;
            if(count <= 0) { clearInterval(timerId); confirmStart(); }
        }, 1000);

        function confirmStart() {
            clearInterval(timerId);
            while(selected.length < 25) {
                let r = Math.floor(Math.random()*100)+1;
                if(!selected.includes(r)) selected.push(r);
            }
            document.getElementById('selection-stage').style.display = 'none';
            document.getElementById('game-stage').style.display = 'block';
            
            // Generate Bingo Table Rows (5x5)
            const tbody = document.getElementById('bingo-body');
            for(let row=0; row<5; row++) {
                let tr = document.createElement('tr');
                for(let col=0; col<5; col++) {
                    let td = document.createElement('td');
                    let val = selected[row * 5 + col];
                    td.id = 'cell-' + val;
                    td.innerText = val;
                    tr.appendChild(td);
                }
                tbody.appendChild(tr);
            }
            drawBall();
        }

        function drawBall() {
            if(called.length >= 100 || isOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            document.getElementById('currentBall').innerText = n;
            document.getElementById('logs').innerHTML += n + ", ";

            let match = document.getElementById('cell-' + n);
            if(match) {
                match.classList.add('marked');
                checkWin();
            }
            if(!isOver) setTimeout(drawBall, 3500);
        }

        function checkWin() {
            const cells = document.querySelectorAll('td');
            let board = [];
            cells.forEach(c => board.push(c.classList.contains('marked')));

            // Check Horizontal
            for (let i = 0; i < 25; i += 5) {
                if (board[i] && board[i+1] && board[i+2] && board[i+3] && board[i+4]) announceWin();
            }
            // Check Vertical
            for (let i = 0; i < 5; i++) {
                if (board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) announceWin();
            }
        }

        function announceWin() {
            if(isOver) return;
            isOver = true;
            document.getElementById('winAlert').style.display = 'block';
            tg.MainButton.setText("INJIFATTEETTA! - MAALLAQA FUDHU").show();
            tg.HapticFeedback.notificationOccurred('success');
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Lakkofsa 25 filadhu, tikeetiin keessan qubeewwan B-I-N-G-O jalatti tarreeffama.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
