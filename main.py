import os
import telebot
from flask import Flask, request, render_template_string
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="or">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Bingo Ethiopia - Professional</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', Roboto, sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
        .container { background: #001f3f; border: 2px solid #00d4ff; border-radius: 20px; padding: 15px; box-shadow: 0 0 30px #00d4ff; max-width: 500px; margin: auto; }
        
        /* Selection Grid 1-100 */
        .grid-100 { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; border: 1px solid #00d4ff; }
        .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 12px 0; border-radius: 6px; font-size: 11px; cursor: pointer; transition: 0.2s; }
        .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; transform: scale(0.9); }

        /* Bingo Table UI */
        .bingo-table { width: 100%; border-collapse: separate; border-spacing: 4px; background: #000; border: 3px solid #ffcc00; border-radius: 15px; overflow: hidden; margin-top: 15px; }
        .bingo-table th { background: #ffcc00; color: #000; padding: 10px; font-size: 24px; font-weight: 900; }
        .bingo-table td { border-radius: 8px; height: 50px; width: 20%; font-size: 18px; font-weight: bold; background: #1a2a44; color: #fff; border: 1px solid #333; }
        .bingo-table td.marked { background: #28a745 !important; border-color: #fff; box-shadow: inset 0 0 12px #fff; animation: pop 0.3s ease; }
        
        @keyframes pop { 0% {transform: scale(1);} 50% {transform: scale(1.2);} 100% {transform: scale(1);} }

        .ball-ui { margin: 20px 0; height: 130px; }
        .ball-letter { font-size: 22px; color: #ffcc00; font-weight: bold; display: block; margin-bottom: -5px; }
        .ball { font-size: 55px; font-weight: 900; background: white; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; border: 6px solid #ffcc00; display: inline-block; box-shadow: 0 0 25px #ffcc00; }
        
        #status-msg { color: #00ffcc; font-size: 14px; font-weight: bold; margin: 10px 0; }
        .win-overlay { display: none; background: #28a745; padding: 20px; border-radius: 15px; border: 4px solid #fff; position: fixed; top: 25%; left: 5%; right: 5%; z-index: 1000; box-shadow: 0 0 50px #000; }
        .btn-main { background: #28a745; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h1 style="color:#ffcc00; margin-bottom:10px; letter-spacing: 2px;">BINGO ETHIOPIA</h1>
    
    <div id="selection-view">
        <p id="status-msg">Lakkofsa 25 filachuun tikeetii kee guuti (1-100):</p>
        <div class="grid-100" id="picker"></div>
        <p style="margin:10px 0; font-weight:bold;">Filatame: <span id="count-display" style="color:#ffcc00;">0/25</span></p>
        <button id="start-btn" class="btn-main" style="display:none;" onclick="startBingo()">TAPHA JALQABI</button>
    </div>

    <div id="game-view" style="display:none;">
        <div class="ball-ui">
            <span id="callLetter" class="ball-letter">...</span>
            <div class="ball" id="callNum">?</div>
        </div>
        
        <table class="bingo-table">
            <thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead>
            <tbody id="bingo-body"></tbody>
        </table>
        
        <div id="history" style="font-size:12px; color:#aaa; margin-top:20px; text-align:left; border-top:1px solid #333; padding-top:10px;">History: </div>
    </div>

    <div id="winArea" class="win-overlay">
        <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
        <p style="font-size:18px;">Sarara tokko guutteetta!</p>
        <button onclick="location.reload()" style="padding:10px; background:white; border:none; border-radius:5px; font-weight:bold;">Taphata Haarawa</button>
    </div>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();
    let selected = [];
    let called = [];
    let isGameOver = false;

    // 1-100 Grid Picker
    const picker = document.getElementById('picker');
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.className = 'n-btn'; b.innerText = i;
        b.onclick = () => {
            if(selected.includes(i)) {
                selected = selected.filter(x => x !== i);
                b.classList.remove('active');
            } else if(selected.length < 25) {
                selected.push(i);
                b.classList.add('active');
            }
            document.getElementById('count-display').innerText = selected.length + "/25";
            document.getElementById('start-btn').style.display = (selected.length === 25) ? 'block' : 'none';
        };
        picker.appendChild(b);
    }

    function startBingo() {
        document.getElementById('selection-view').style.display = 'none';
        document.getElementById('game-view').style.display = 'block';
        
        const tbody = document.getElementById('bingo-body');
        // Arrange selected numbers into 5x5 grid
        for(let r=0; r<5; r++) {
            let tr = document.createElement('tr');
            for(let c=0; c<5; c++) {
                let td = document.createElement('td');
                let val = selected[r * 5 + c];
                td.id = 'cell-' + val;
                td.innerText = val;
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        setTimeout(draw, 2000);
    }

    function getLetter(n) {
        if(n <= 20) return "B"; if(n <= 40) return "I"; if(n <= 60) return "N"; if(n <= 80) return "G"; return "O";
    }

    function draw() {
        if(called.length >= 100 || isGameOver) return;
        let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
        called.push(n);

        let L = getLetter(n);
        document.getElementById('callLetter').innerText = L;
        document.getElementById('callNum').innerText = n;
        document.getElementById('history').innerHTML += L + "-" + n + ", ";

        let match = document.getElementById('cell-' + n);
        if(match) {
            match.classList.add('marked');
            checkBingo();
        }
        if(!isGameOver) setTimeout(draw, 3500);
    }

    function checkBingo() {
        const board = selected.map(n => document.getElementById('cell-'+n).classList.contains('marked'));
        // Rows & Columns
        for(let i=0; i<5; i++) {
            // Horizontal
            if(board[i*5] && board[i*5+1] && board[i*5+2] && board[i*5+3] && board[i*5+4]) doWin();
            // Vertical
            if(board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) doWin();
        }
    }

    function doWin() {
        if(isGameOver) return;
        isGameOver = true;
        document.getElementById('winArea').style.display = 'block';
        tg.MainButton.setText("BINGO! - FUDHU").show();
        tg.HapticFeedback.notificationOccurred('success');
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Lakkofsa 25 filachuun karteellaa keessan kuta.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
