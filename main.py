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
        <title>Bingo Ethiopia - Winner Display</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #001f3f; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: #003366; padding: 15px; border-radius: 15px; border: 1px solid #00d4ff; }
            h1 { color: #ffcc00; font-size: 22px; margin: 5px; }
            
            /* Grid */
            .grid-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin: 15px 0; max-height: 250px; overflow-y: auto; padding: 5px; background: #001a33; border-radius: 10px; }
            .num-btn { background: #004080; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 5px; cursor: pointer; }
            .num-btn.selected { background: #ffcc00; color: #000; font-weight: bold; }
            
            .summary-box { background: #002b55; padding: 10px; border-radius: 8px; margin: 10px 0; font-size: 14px; border-left: 5px solid #ffcc00; text-align: left; }
            .timer { font-size: 18px; color: #ff4444; font-weight: bold; }
            
            /* Game UI */
            .call-circle { font-size: 50px; font-weight: bold; background: #fff; color: #003366; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; display: inline-block; margin: 10px; border: 4px solid #ffcc00; }
            .win-box { display: none; background: #28a745; color: white; padding: 15px; border-radius: 10px; margin-top: 15px; border: 2px solid #fff; animation: bounce 0.5s infinite alternate; }
            @keyframes bounce { from { transform: scale(1); } to { transform: scale(1.05); } }
            
            .history { font-size: 12px; background: #001a33; padding: 10px; border-radius: 8px; height: 70px; overflow-y: auto; margin-top: 10px; }
            .win-num-highlight { color: #ffcc00; font-weight: bold; text-decoration: underline; }
        </style>
    </head>
    <body>

    <div class="card">
        <h1>BINGO ETHIOPIA</h1>
        
        <div id="selection-screen">
            <div class="timer" id="timer">01:00</div>
            <div class="grid-container" id="grid"></div>
            <div class="summary-box">
                <strong>Karteelaa Filatame:</strong><br>
                <span id="selected-list">Hiriira filadhu...</span>
            </div>
            <button style="background: #28a745; color: white; padding: 15px; border: none; border-radius: 10px; width: 100%; font-size: 18px; font-weight: bold;" onclick="confirmSelection()">TAPHA JALQABI</button>
        </div>

        <div id="game-screen" style="display:none;">
            <p style="color: #ffcc00;">[ LINE 1 MODE ]</p>
            <div id="call-area">
                <span id="currentLetter" style="font-size: 24px; color: #ffcc00; display: block;">WAIT...</span>
                <div class="call-circle" id="currentNum">?</div>
            </div>

            <div id="winner-display" class="win-box">
                <h2 style="margin:0;">🎊 BINGO! 🎊</h2>
                <p style="margin:5px 0;">Lakkofsa Injifate: <span id="win-number-text" style="font-size: 24px; font-weight: bold;"></span></p>
                <p>Maallaqa kee fudhu!</p>
            </div>

            <p style="margin-top:10px;">Karteelaa Kee: <span id="myTicketsDisp" style="color:#00ffcc;"></span></p>
            <div class="history" id="historyBox">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        
        let selectedNumbers = [];
        let timerSeconds = 60;
        let called = [];
        let isGameOver = false;

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
                document.getElementById('selected-list').innerText = selectedNumbers.sort((a,b)=>a-b).join(', ');
            };
            grid.appendChild(btn);
        }

        let countdown = setInterval(() => {
            timerSeconds--;
            let m = Math.floor(timerSeconds/60), s = timerSeconds%60;
            document.getElementById('timer').innerText = `${m<10?'0':''}${m}:${s<10?'0':''}${s}`;
            if (timerSeconds <= 0) confirmSelection();
        }, 1000);

        function confirmSelection() {
            if (selectedNumbers.length === 0) return alert("Karteelaa filadhu!");
            clearInterval(countdown);
            document.getElementById('selection-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'block';
            document.getElementById('myTicketsDisp').innerText = selectedNumbers.join(', ');
            nextCall();
        }

        function getLetter(n) {
            if (n <= 20) return "B"; if (n <= 40) return "I"; if (n <= 60) return "N"; if (n <= 80) return "G"; return "O";
        }

        function nextCall() {
            if (called.length >= 100 || isGameOver) return;
            let n;
            do { n = Math.floor(Math.random() * 100) + 1; } while (called.includes(n));
            called.push(n);
            let L = getLetter(n);
            
            document.getElementById('currentLetter').innerText = L;
            document.getElementById('currentNum').innerText = n;
            
            let histSpan = selectedNumbers.includes(n) ? `<span class="win-num-highlight">${L}-${n}</span>` : `${L}-${n}`;
            document.getElementById('historyBox').innerHTML += histSpan + ", ";

            if (selectedNumbers.includes(n)) {
                isGameOver = true;
                document.getElementById('winner-display').style.display = 'block';
                document.getElementById('win-number-text').innerText = `${L}-${n}`;
                document.getElementById('call-area').style.opacity = "0.5";
                tg.MainButton.setText("INJIFATE - MAALLAQA FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(nextCall, 3500);
            }
        }
    </script>
    </body>
    </html>
    """

# 3. BOT & WEBHOOK
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Baga nagaan dhuftan! Bingo Ethiopia Line 1 Win Mode.\nKarteelaa 100 keessaa filadhu.", 
                     reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

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
