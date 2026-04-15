import os
import telebot
import time
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
        <title>Bingo Ethiopia - Live 24/7</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 20px #00d4ff; }
            
            /* Ball Style */
            .ball-zone { margin: 15px 0; }
            .ball-letter { font-size: 24px; color: #ffcc00; font-weight: bold; display: block; margin-bottom: -10px; }
            .ball-num { font-size: 60px; font-weight: bold; background: white; color: #001f3f; width: 110px; height: 110px; line-height: 110px; border-radius: 50%; border: 6px solid #ffcc00; display: inline-block; box-shadow: 0 0 25px #ffcc00; }

            /* Bingo Table */
            .bingo-card { width: 100%; border-collapse: collapse; background: #000; border: 3px solid #ffcc00; border-radius: 10px; overflow: hidden; }
            .bingo-card th { background: #ffcc00; color: #000; padding: 10px 0; font-size: 22px; }
            .bingo-card td { border: 1px solid #333; height: 50px; width: 20%; font-size: 18px; font-weight: bold; background: #1a2a44; }
            .bingo-card td.marked { background: #28a745; color: white; box-shadow: inset 0 0 10px #fff; transform: scale(0.95); transition: 0.4s; }

            .status-box { background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #00d4ff; }
            .timer-text { font-size: 22px; color: #ff4444; font-weight: bold; }
            .win-msg { display: none; background: #28a745; padding: 20px; border-radius: 15px; border: 3px solid #fff; position: fixed; top: 20%; left: 10%; right: 10%; z-index: 100; box-shadow: 0 0 50px #000; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA LIVE</h2>
        
        <div class="status-box">
            <div id="setup-view">
                <div class="timer-text">Cufamuuf: <span id="timer">40</span>s</div>
                <p style="font-size:12px;">Tikeetiin keessan ofumaan kallaattiin qophaa'a...</p>
            </div>
            <div id="game-info" style="display:none;">
                <p style="color:#00ffcc; margin:0;">Taphni deemaa jira...</p>
            </div>
        </div>

        <div class="ball-zone">
            <span class="ball-letter" id="callLetter">...</span>
            <div class="ball-num" id="callNum">?</div>
        </div>

        <table class="bingo-card">
            <thead>
                <tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr>
            </thead>
            <tbody id="bingo-body">
                </tbody>
        </table>

        <div id="winArea" class="win-msg">
            <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
            <p>SARARRI GUUTAMEERA!</p>
            <button onclick="location.reload()" style="padding:10px; border-radius:5px; border:none; background:white; font-weight:bold;">Taphatti Deebi'i</button>
        </div>

        <div id="history" style="font-size:11px; color:#aaa; margin-top:20px; text-align:left;">Galmee: </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timeLeft = 40;
        let isGameOver = false;
        let calledNumbers = [];
        let myNumbers = [];

        // 1. Tikeetii qopheessuu (B: 1-20, I: 21-40, ...)
        function createTicket() {
            const tbody = document.getElementById('bingo-body');
            let ticketData = [];
            for(let row=0; row<5; row++) {
                let tr = document.createElement('tr');
                for(let col=0; col<5; col++) {
                    let min = (col * 20) + 1;
                    let max = (col * 20) + 20;
                    let val;
                    do { val = Math.floor(Math.random() * (max - min + 1)) + min; } while(ticketData.includes(val));
                    ticketData.push(val);
                    
                    let td = document.createElement('td');
                    td.id = 'cell-' + val;
                    td.innerText = val;
                    tr.appendChild(td);
                }
                tbody.appendChild(tr);
            }
            myNumbers = ticketData;
        }

        createTicket();

        // 2. Timer Logic (Hojiirra itti fufa)
        let timerId = setInterval(() => {
            timeLeft--;
            document.getElementById('timer').innerText = timeLeft;
            if(timeLeft <= 0) {
                clearInterval(timerId);
                document.getElementById('setup-view').style.display = 'none';
                document.getElementById('game-info').style.display = 'block';
                startDrawing();
            }
        }, 1000);

        function getLetter(n) {
            if(n <= 20) return "B";
            if(n <= 40) return "I";
            if(n <= 60) return "N";
            if(n <= 80) return "G";
            return "O";
        }

        // 3. Drawing Logic
        function startDrawing() {
            if(calledNumbers.length >= 100 || isGameOver) return;
            
            let n;
            do { n = Math.floor(Math.random() * 100) + 1; } while(calledNumbers.includes(n));
            calledNumbers.push(n);
            
            let L = getLetter(n);
            document.getElementById('callLetter').innerText = L;
            document.getElementById('callNum').innerText = n;
            document.getElementById('history').innerHTML += L + "-" + n + ", ";

            // Mark check
            let match = document.getElementById('cell-' + n);
            if(match) {
                match.classList.add('marked');
                checkBingo();
            }

            if(!isGameOver) setTimeout(startDrawing, 3000);
        }

        function checkBingo() {
            const cells = document.querySelectorAll('td');
            let board = [];
            cells.forEach(c => board.push(c.classList.contains('marked')));

            // Check Horizontal Rows
            for (let i = 0; i < 25; i += 5) {
                if (board[i] && board[i+1] && board[i+2] && board[i+3] && board[i+4]) win();
            }
            // Check Vertical Columns
            for (let i = 0; i < 5; i++) {
                if (board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) win();
            }
        }

        function win() {
            isGameOver = true;
            document.getElementById('winArea').style.display = 'block';
            tg.MainButton.setText("BINGO! - MAALLAQA FUDHU").show();
            tg.HapticFeedback.notificationOccurred('success');
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Bingo Ethiopia Real-time eegaleera.\nTikeetiin keessan ofumaan qophaa'ee 40 sec booda lakkofsi waamama.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
