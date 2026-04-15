import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
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
        <title>Bingo Ethiopia - Line 1 Auto</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 15px #00d4ff; }
            h1 { color: #ffcc00; font-size: 22px; margin-bottom: 10px; }
            
            /* Bingo Table Style */
            .bingo-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
            .bingo-table th { background: #ffcc00; color: #000; padding: 5px; font-size: 16px; border: 1px solid #000; }
            .bingo-table td { border: 1px solid #007bff; height: 45px; font-size: 18px; font-weight: bold; background: #1a2a44; color: #fff; }
            .bingo-table td.marked { background: #28a745; color: white; border: 2px solid #fff; }

            .timer-box { font-size: 18px; color: #ff4444; font-weight: bold; margin-bottom: 10px; }
            .call-circle { font-size: 45px; font-weight: bold; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; margin: 10px; }
            
            .win-msg { display: none; background: #28a745; padding: 10px; border-radius: 10px; border: 2px solid #fff; margin-top: 10px; font-weight: bold; font-size: 20px; }
            .history { background: rgba(0,0,0,0.5); padding: 5px; border-radius: 8px; height: 50px; overflow-y: auto; font-size: 12px; margin-top: 10px; color: #ccc; }
        </style>
    </head>
    <body>
    <div class="card">
        <h1>BINGO ETHIOPIA</h1>
        
        <div id="selection-screen">
            <div class="timer-box">Hafe: <span id="timer">40</span>s</div>
            <p style="font-size: 13px;">Tikeetiin keessan ofumaan ni qophaa'a...</p>
            <table class="bingo-table">
                <tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr>
                <tr>
                    <td id="cell-B">?</td><td id="cell-I">?</td><td id="cell-N">?</td><td id="cell-G">?</td><td id="cell-O">?</td>
                </tr>
            </table>
            <p style="font-size:11px; color:#aaa;">(Yeroon yoo dhumu taphni ofumaan eegala)</p>
        </div>

        <div id="game-screen" style="display:none;">
            <table class="bingo-table">
                <tr><th>B</th><th>I</th><th>N</th><th>G</th><th>O</th></tr>
                <tr>
                    <td id="game-B"></td><td id="game-I"></td><td id="game-N"></td><td id="game-G"></td><td id="game-O"></td>
                </tr>
            </table>

            <div id="call-box">
                <span id="curL" style="font-size: 24px; color: #ffcc00; display: block; font-weight: bold;">...</span>
                <div class="call-circle" id="curN">?</div>
            </div>

            <div class="win-msg" id="win-area">
                🎊 BINGO! LINE 1 🎊<br>
                <span id="win-num" style="font-size: 24px;"></span>
            </div>

            <div class="history" id="hist">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timerSeconds = 40; // 40 seconds sirreeffame
        let called = [];
        let isGameOver = false;
        let hits = 0;

        // Karteellaa ofumaan uumuu (Tikeeti tokko)
        let myTicket = {
            'B': Math.floor(Math.random() * 20) + 1,
            'I': Math.floor(Math.random() * 20) + 21,
            'N': Math.floor(Math.random() * 20) + 41,
            'G': Math.floor(Math.random() * 20) + 61,
            'O': Math.floor(Math.random() * 20) + 81
        };

        // UI irratti tikeetii agarsiisuu
        const cells = ['B', 'I', 'N', 'G', 'O'];
        cells.forEach(c => {
            document.getElementById('cell-' + c).innerText = myTicket[c];
            document.getElementById('game-' + c).innerText = myTicket[c];
        });

        // 40 Second Timer
        let countdown = setInterval(() => {
            timerSeconds--;
            document.getElementById('timer').innerText = timerSeconds;
            if (timerSeconds <= 0) {
                clearInterval(countdown);
                startBingoAuto();
            }
        }, 1000);

        function startBingoAuto() {
            document.getElementById('selection-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'block';
            runGame();
        }

        function getLetter(n) {
            if (n <= 20) return "B"; if (n <= 40) return "I"; if (n <= 60) return "N"; if (n <= 80) return "G"; return "O";
        }

        function runGame() {
            if (called.length >= 100 || isGameOver) return;
            
            let n; 
            do { n = Math.floor(Math.random() * 100) + 1; } while (called.includes(n));
            called.push(n);
            
            let L = getLetter(n);
            document.getElementById('curL').innerText = L;
            document.getElementById('curN').innerText = n;
            document.getElementById('hist').innerHTML += L + "-" + n + ", ";

            // Match Logic
            cells.forEach(c => {
                if (myTicket[c] === n) {
                    document.getElementById('game-' + c).classList.add('marked');
                    hits++;
                }
            });

            // Line 1 Win Logic (Tokko yoo guute)
            if (hits >= 1 && !isGameOver) {
                isGameOver = true;
                document.getElementById('win-area').style.display = 'block';
                document.getElementById('win-num').innerText = L + "-" + n;
                tg.MainButton.setText("BINGO - MAALLAQA FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(runGame, 3500);
            }
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Tikeetiin keessan qophaa'eera.\nSekondii 40 booda ofumaan eegala.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/set_webhook")
def set_webhook():
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Done", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
