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
        <title>Bingo Ethiopia - Automated</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: linear-gradient(145deg, #001f3f, #003366); padding: 20px; border-radius: 20px; border: 2px solid #00d4ff; box-shadow: 0 0 20px rgba(0,212,255,0.3); }
            h1 { color: #ffcc00; font-size: 26px; text-transform: uppercase; letter-spacing: 3px; margin: 10px 0; }
            
            /* Selection Grid Style */
            .grid-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin: 15px 0; max-height: 280px; overflow-y: auto; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 12px; border: 1px solid #007bff; }
            .num-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 12px 0; border-radius: 8px; font-size: 16px; cursor: pointer; }
            .num-btn.selected { background: #ffcc00; color: #000; font-weight: bold; transform: scale(1.1); box-shadow: 0 0 10px #ffcc00; }
            
            .timer-box { font-size: 22px; color: #ff4444; font-weight: bold; background: #1a0000; padding: 10px; border-radius: 10px; border: 1px solid #ff4444; display: inline-block; margin-bottom: 10px; }
            
            /* Game UI */
            .call-circle { font-size: 60px; font-weight: bold; background: radial-gradient(circle, #fff, #ddd); color: #003366; width: 110px; height: 110px; line-height: 110px; border-radius: 50%; display: inline-block; border: 5px solid #ffcc00; box-shadow: 0 0 25px #ffcc00; }
            
            .win-box { display: none; background: #28a745; color: white; padding: 20px; border-radius: 15px; margin-top: 20px; border: 3px solid #fff; }
            .history { font-size: 14px; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; height: 80px; overflow-y: auto; margin-top: 15px; border: 1px solid #333; }
        </style>
    </head>
    <body>

    <div class="card">
        <h1>BINGO ETHIOPIA</h1>
        
        <div id="selection-screen">
            <div class="timer-box">Hafe: <span id="timer">01:00</span></div>
            <p style="font-size:14px; color:#00ffcc;">Karteelaa Kee Filadhu (Hanga 10):</p>
            <div class="grid-container" id="grid"></div>
            <div id="selected-summary" style="font-size:12px; color:#aaa;">Filatame: ---</div>
            <p style="font-size:11px; color:#ff4444; margin-top:10px;">*Yeroon yoo dhumu ofumaan eegala!</p>
        </div>

        <div id="game-screen" style="display:none;">
            <div id="call-area">
                <span id="currentLetter" style="font-size: 28px; color: #ffcc00; display: block; font-weight: bold;">WAAMAMAA...</span>
                <div class="call-circle" id="currentNum">?</div>
            </div>

            <div id="winner-display" class="win-box">
                <h2 style="margin:0;">🎊 BINGO! 🎊</h2>
                <p>Lakk. Injifate: <span id="win-number-text" style="font-size: 32px; font-weight: bold;"></span></p>
            </div>

            <p style="margin-top:20px; font-weight:bold;">Tikeetii Kee: <span id="myTicketsDisp" style="color:#00ffcc;"></span></p>
            <div class="history" id="historyBox">Galmee (History): </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        
        let selectedNumbers = [];
        let timerSeconds = 60;
        let called = [];
        let isGameOver = false;

        // 1. Grid uumuu
        const grid = document.getElementById('grid');
        for (let i = 1; i <= 100; i++) {
            let btn = document.createElement('button');
            btn.className = 'num-btn';
            btn.innerText = i;
            btn.onclick = () => {
                if (selectedNumbers.includes(i)) {
                    selectedNumbers = selectedNumbers.filter(n => n !== i);
                    btn.classList.remove('selected');
                } else if (selectedNumbers.length < 10) {
                    selectedNumbers.push(i);
                    btn.classList.add('selected');
                }
                document.getElementById('selected-summary').innerText = "Filatame: " + selectedNumbers.sort((a,b)=>a-b).join(', ');
            };
            grid.appendChild(btn);
        }

        // 2. Automated Timer (Namni ofiin eegalchiisuu hin danda'u)
        let countdown = setInterval(() => {
            timerSeconds--;
            let m = Math.floor(timerSeconds/60), s = timerSeconds%60;
            document.getElementById('timer').innerText = `${m<10?'0':''}${m}:${s<10?'0':''}${s}`;
            
            if (timerSeconds <= 0) {
                clearInterval(countdown);
                startBingoAuto();
            }
        }, 1000);

        function startBingoAuto() {
            document.getElementById('selection-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'block';
            document.getElementById('myTicketsDisp').innerText = selectedNumbers.length > 0 ? selectedNumbers.join(', ') : "Filannoo hin qabu";
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
            
            document.getElementById('currentLetter').innerText = L;
            document.getElementById('currentNum').innerText = n;
            document.getElementById('historyBox').innerHTML += `${L}-${n}, `;

            // Winner Logic (Line 1)
            if (selectedNumbers.includes(n)) {
                isGameOver = true;
                document.getElementById('winner-display').style.display = 'block';
                document.getElementById('win-number-text').innerText = `${L}-${n}`;
                tg.MainButton.setText("INJIFATTEETTA!").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(runGame, 4000);
            }
        }
    </script>
    </body>
    </html>
    """

# 3. BOT
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bingo Ethiopia B-I-N-G-O Style.\n\nTikeetii kee filachuuf daqiiqaa 1 qabda. Sana booda ofumaan eegala.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL)))
    )

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/set_webhook")
def set_webhook():
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Done", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
