import os
import telebot
import random
from flask import Flask, request, render_template_string
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# HTML Interface (Mini App)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="or">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Bingo Ethiopia Live</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; overflow-x: hidden; }
        .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 20px #00d4ff; max-width: 400px; margin: auto; }
        .ball-zone { margin: 15px 0; min-height: 150px; }
        .ball-letter { font-size: 28px; color: #ffcc00; font-weight: bold; display: block; }
        .ball-num { font-size: 65px; font-weight: bold; background: white; color: #001f3f; width: 110px; height: 110px; line-height: 110px; border-radius: 50%; border: 6px solid #ffcc00; display: inline-block; box-shadow: 0 0 25px #ffcc00; }
        .bingo-card { width: 100%; border-collapse: collapse; background: #000; border: 3px solid #ffcc00; border-radius: 10px; overflow: hidden; margin-top: 10px; }
        .bingo-card th { background: #ffcc00; color: #000; padding: 8px 0; font-size: 20px; }
        .bingo-card td { border: 1px solid #333; height: 45px; width: 20%; font-size: 16px; font-weight: bold; background: #1a2a44; }
        .bingo-card td.marked { background: #28a745; color: white; box-shadow: inset 0 0 10px #fff; }
        .timer-box { font-size: 20px; color: #ff4444; font-weight: bold; margin-bottom: 10px; }
        .history { font-size: 12px; color: #aaa; margin-top: 15px; text-align: left; padding: 5px; background: rgba(0,0,0,0.3); border-radius: 5px; height: 40px; overflow-y: auto; }
    </style>
</head>
<body>
<div class="card">
    <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA</h2>
    
    <div id="setup">
        <div class="timer-box">Cufamuuf: <span id="timer">40</span>s</div>
        <p style="font-size:12px;">Tikeetiin kee ofumaan qophaa'aa jira...</p>
    </div>

    <div id="game-ui" style="display:none;">
        <div class="ball-zone">
            <span class="ball-letter" id="callLetter">...</span>
            <div class="ball-num" id="callNum">?</div>
        </div>
        <table class="bingo-card">
            <thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead>
            <tbody id="bingo-body"></tbody>
        </table>
        <div class="history" id="history">Galmee: </div>
    </div>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();
    let timeLeft = 40;
    let called = [];
    let myNumbers = [];
    let isOver = false;

    // 1. Tikeetii uumuu
    function createTicket() {
        const tbody = document.getElementById('bingo-body');
        let html = "";
        let tempNums = [];
        for(let r=0; r<5; r++) {
            html += "<tr>";
            for(let c=0; c<5; c++) {
                let min = (c * 20) + 1;
                let max = (c * 20) + 20;
                let n;
                do { n = Math.floor(Math.random() * (max - min + 1)) + min; } while(tempNums.includes(n));
                tempNums.push(n);
                html += `<td id="cell-${n}">${n}</td>`;
            }
            html += "</tr>";
        }
        tbody.innerHTML = html;
        myNumbers = tempNums;
    }
    createTicket();

    // 2. Timer
    let tInterval = setInterval(() => {
        timeLeft--;
        document.getElementById('timer').innerText = timeLeft;
        if(timeLeft <= 0) {
            clearInterval(tInterval);
            document.getElementById('setup').style.display = 'none';
            document.getElementById('game-ui').style.display = 'block';
            draw();
        }
    }, 1000);

    function getLetter(n) {
        if(n <= 20) return "B"; if(n <= 40) return "I"; if(n <= 60) return "N"; if(n <= 80) return "G"; return "O";
    }

    // 3. Draw
    function draw() {
        if(called.length >= 100 || isOver) return;
        let n;
        do { n = Math.floor(Math.random() * 100) + 1; } while(called.includes(n));
        called.push(n);

        let L = getLetter(n);
        document.getElementById('callLetter').innerText = L;
        document.getElementById('callNum').innerText = n;
        document.getElementById('history').innerHTML += L + "-" + n + ", ";

        let cell = document.getElementById('cell-' + n);
        if(cell) {
            cell.classList.add('marked');
            checkWin();
        }
        setTimeout(draw, 3500);
    }

    function checkWin() {
        let board = myNumbers.map(n => document.getElementById('cell-'+n).classList.contains('marked'));
        // Horizontal & Vertical check
        for(let i=0; i<5; i++) {
            // Horizontal
            if(board[i*5] && board[i*5+1] && board[i*5+2] && board[i*5+3] && board[i*5+4]) win();
            // Vertical
            if(board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) win();
        }
    }

    function win() {
        if(isOver) return;
        isOver = true;
        tg.showConfirm("BINGO! Inni jalqabaa sarara guuteera. Maallaqa fudhu?");
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
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Bingo Ethiopia Real-time eegaleera.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
