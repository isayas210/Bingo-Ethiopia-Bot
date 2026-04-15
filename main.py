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
    <title>Bingo Ethiopia - Ticket Picker</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
        .container { background: #001f3f; border: 2px solid #00d4ff; border-radius: 20px; padding: 15px; box-shadow: 0 0 25px #00d4ff; max-width: 500px; margin: auto; }
        
        /* Selection Grid 1-100 */
        .grid-100 { display: grid; grid-template-columns: repeat(10, 1fr); gap: 5px; max-height: 350px; overflow-y: auto; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 12px; border: 2px solid #00d4ff; }
        .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 12px 0; border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; }
        .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; border-color: #fff; transform: scale(0.9); }

        /* Bingo Card Display */
        .ticket-wrapper { margin-top: 20px; display: flex; flex-direction: column; gap: 20px; }
        .bingo-card { width: 100%; border-collapse: separate; border-spacing: 3px; background: #000; border: 3px solid #ffcc00; border-radius: 12px; overflow: hidden; }
        .bingo-card th { background: #ffcc00; color: #000; padding: 8px; font-size: 20px; font-weight: 900; }
        .bingo-card td { border-radius: 5px; height: 45px; width: 20%; font-size: 16px; font-weight: bold; background: #1a2a44; color: #fff; border: 1px solid #333; }
        .bingo-card td.marked { background: #28a745 !important; box-shadow: inset 0 0 10px #fff; animation: pop 0.3s ease; }
        
        @keyframes pop { 0% {transform: scale(1);} 50% {transform: scale(1.15);} 100% {transform: scale(1);} }

        .ball-box { margin: 20px 0; min-height: 120px; }
        .ball { font-size: 50px; font-weight: 900; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; border: 5px solid #ffcc00; display: inline-block; box-shadow: 0 0 20px #ffcc00; }
        .ball-letter { font-size: 20px; color: #ffcc00; font-weight: bold; display: block; margin-bottom: -5px; }
        
        .btn-play { background: #28a745; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; font-size: 18px; cursor: pointer; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .win-msg { display: none; background: #28a745; padding: 20px; border-radius: 15px; border: 4px solid #fff; position: fixed; top: 25%; left: 5%; right: 5%; z-index: 1000; }
    </style>
</head>
<body>
<div class="container">
    <h2 style="color:#ffcc00; margin-bottom:10px;">BINGO ETHIOPIA</h2>
    
    <div id="selection-view">
        <p style="font-size:14px; color:#00ffcc;">Tikeetiwwan kuttuuf lakkofsota cuqaasi:</p>
        <div class="grid-100" id="picker-grid"></div>
        <p style="margin:15px 0;">Tikeetii Filatame: <span id="count" style="color:#ffcc00; font-weight:bold;">0</span></p>
        <button id="play-btn" class="btn-play" style="display:none;" onclick="startDrawing()">TAPHA JALQABI</button>
    </div>

    <div id="game-view" style="display:none;">
        <div class="ball-box">
            <span id="callLetter" class="ball-letter">...</span>
            <div class="ball" id="callNum">?</div>
        </div>
        <div id="ticket-list" class="ticket-wrapper"></div>
        <div id="history" style="font-size:11px; color:#aaa; margin-top:20px; text-align:left; border-top:1px solid #333; padding-top:10px;">History: </div>
    </div>

    <div id="winArea" class="win-msg">
        <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
        <p>Tikeetii tokko irratti sarara guutteetta!</p>
        <button onclick="location.reload()" style="padding:10px; border-radius:5px; border:none; background:white; font-weight:bold;">Haarawa Jalqabi</button>
    </div>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();
    let selectedTickets = [];
    let calledNumbers = [];
    let gameActive = false;
    let isWinner = false;

    // Create 1-100 Grid
    const picker = document.getElementById('picker-grid');
    for(let i=1; i<=100; i++) {
        let btn = document.createElement('button');
        btn.className = 'n-btn'; btn.innerText = i;
        btn.onclick = () => {
            if(selectedTickets.includes(i)) {
                selectedTickets = selectedTickets.filter(x => x !== i);
                btn.classList.remove('active');
            } else {
                selectedTickets.push(i);
                btn.classList.add('active');
            }
            document.getElementById('count').innerText = selectedTickets.length;
            document.getElementById('play-btn').style.display = (selectedTickets.length > 0) ? 'block' : 'none';
        };
        picker.appendChild(btn);
    }

    function startDrawing() {
        document.getElementById('selection-view').style.display = 'none';
        document.getElementById('game-view').style.display = 'block';
        
        const container = document.getElementById('ticket-list');
        selectedTickets.forEach(tNum => {
            // Generate 25 random numbers for each ticket selected
            let tData = [];
            while(tData.length < 25) {
                let r = Math.floor(Math.random() * 100) + 1;
                if(!tData.includes(r)) tData.push(r);
            }
            
            let html = `<div style="margin-bottom:10px; font-weight:bold; color:#ffcc00;">Tikeetii #${tNum}</div>
                        <table class="bingo-card" id="card-${tNum}">
                        <thead><tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr></thead><tbody>`;
            for(let r=0; r<5; r++) {
                html += "<tr>";
                for(let c=0; c<5; c++) {
                    let val = tData[r*5 + c];
                    html += `<td id="t${tNum}-n${val}">${val}</td>`;
                }
                html += "</tr>";
            }
            html += "</tbody></table>";
            let div = document.createElement('div');
            div.innerHTML = html;
            container.appendChild(div);
        });
        
        gameActive = true;
        setTimeout(draw, 2000);
    }

    function getLetter(n) {
        if(n <= 20) return "B"; if(n <= 40) return "I"; if(n <= 60) return "N"; if(n <= 80) return "G"; return "O";
    }

    function draw() {
        if(!gameActive || isWinner || calledNumbers.length >= 100) return;
        
        let n;
        do { n = Math.floor(Math.random() * 100) + 1; } while(calledNumbers.includes(n));
        calledNumbers.push(n);

        let L = getLetter(n);
        document.getElementById('callLetter').innerText = L;
        document.getElementById('callNum').innerText = n;
        document.getElementById('history').innerHTML += L + "-" + n + ", ";

        // Check all tickets for this number
        selectedTickets.forEach(tNum => {
            let cell = document.getElementById(`t${tNum}-n${n}`);
            if(cell) {
                cell.classList.add('marked');
                checkBingo(tNum);
            }
        });

        if(!isWinner) setTimeout(draw, 3500);
    }

    function checkBingo(tNum) {
        const table = document.getElementById(`card-${tNum}`);
        const cells = table.querySelectorAll('td');
        let board = Array.from(cells).map(c => c.classList.contains('marked'));

        for(let i=0; i<5; i++) {
            // Horizontal
            if(board[i*5] && board[i*5+1] && board[i*5+2] && board[i*5+3] && board[i*5+4]) win();
            // Vertical
            if(board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) win();
        }
    }

    function win() {
        isWinner = true;
        document.getElementById('winArea').style.display = 'block';
        tg.MainButton.setText("BINGO! - INJIFATTEETTA").show();
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
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Grid 1-100 irraa tikeetii barbaaddan filadhaatii kuta.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
