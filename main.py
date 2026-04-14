import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. MINI APP INTERFACE
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia - Selection</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #001f3f; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: #003366; padding: 15px; border-radius: 15px; border: 1px solid #00d4ff; }
            h1 { color: #ffcc00; font-size: 22px; margin: 5px; }
            
            /* Grid Selection */
            .grid-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin: 15px 0; max-height: 300px; overflow-y: auto; padding: 5px; background: #001a33; border-radius: 10px; }
            .num-btn { background: #004080; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 5px; cursor: pointer; font-size: 14px; }
            .num-btn.selected { background: #ffcc00; color: #000; font-weight: bold; border-color: #fff; }
            
            .timer { font-size: 18px; color: #ff4444; font-weight: bold; margin: 10px 0; }
            .info-text { font-size: 13px; color: #00ffcc; }
            .btn-start { background: #28a745; color: white; padding: 15px; border: none; border-radius: 10px; width: 100%; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            
            /* Game Display */
            .call-display { margin: 20px 0; display: none; }
            .letter { font-size: 30px; font-weight: bold; color: #ffcc00; display: block; }
            .number-circle { font-size: 50px; font-weight: bold; background: #fff; color: #003366; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; display: inline-block; margin: 10px; box-shadow: 0 0 20px #ffcc00; }
            .history { font-size: 12px; background: #001a33; padding: 10px; border-radius: 8px; height: 80px; overflow-y: auto; text-align: left; margin-top: 10px; color: #ccc; }
        </style>
    </head>
    <body>

    <div class="card">
        <h1>BINGO ETHIOPIA</h1>
        
        <div id="selection-screen">
            <p class="info-text">Tikeetii kee filadhu (Hanga 10):</p>
            <div class="timer" id="timer">01:00</div>
            <div class="grid-container" id="grid"></div>
            <p id="counter">Filatame: 0/10</p>
            <button class="btn-start" id="playBtn" onclick="confirmSelection()">TAPHA JALQABI</button>
        </div>

        <div id="game-screen" style="display:none;">
            <div class="call-display" id="callDisplay" style="display:block;">
                <span class="letter" id="currentLetter">JALQABAA...</span>
                <div class="number-circle" id="currentNum">?</div>
            </div>
            <p>Tikeetota Kee: <span id="myTicketsDisp" style="color:#ffcc00;"></span></p>
            <div class="history" id="historyBox">History: </div>
            <div id="winMsg" style="color:#2ecc71; font-weight:bold; font-size:20px; margin-top:10px;"></div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        
        let selectedNumbers = [];
        let timerSeconds = 60;
        let called = [];

        // 1. Lakkofsa 1-100 uumuu
        const grid = document.getElementById('grid');
        for (let i = 1; i <= 100; i++) {
            let btn = document.createElement('button');
            btn.className = 'num-btn';
            btn.innerText = i;
            btn.onclick = () => toggleNumber(i, btn);
            grid.appendChild(btn);
        }

        function toggleNumber(num, btn) {
            if (selectedNumbers.includes(num)) {
                selectedNumbers = selectedNumbers.filter(n => n !== num);
                btn.classList.remove('selected');
            } else {
                if (selectedNumbers.length < 10) {
                    selectedNumbers.push(num);
                    btn.classList.add('selected');
                } else {
                    alert("Tikeetii 10 qofa filachuu dandeessa!");
                }
            }
            document.getElementById('counter').innerText = `Filatame: ${selectedNumbers.length}/10`;
        }

        // 2. Timer jalqabsiisuu
        let countdown = setInterval(() => {
            timerSeconds--;
            let mins = Math.floor(timerSeconds / 60);
            let secs = timerSeconds % 60;
            document.getElementById('timer').innerText = `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
            if (timerSeconds <= 0) {
                clearInterval(countdown);
                confirmSelection();
            }
        }, 1000);

        function confirmSelection() {
            if (selectedNumbers.length === 0) {
                alert("Maaloo tikeetii tokko filadhu!");
                return;
            }
            clearInterval(countdown);
            document.getElementById('selection-screen').style.display = 'none';
            document.getElementById('game-screen').style.display = 'block';
            document.getElementById('myTicketsDisp').innerText = selectedNumbers.join(', ');
            nextCall();
        }

        function getLetter(n) {
            if (n <= 20) return "B";
            if (n <= 40) return "I";
            if (n <= 60) return "N";
            if (n <= 80) return "G";
            return "O";
        }

        function nextCall() {
            if (called.length >= 100) return;
            let n;
            do { n = Math.floor(Math.random() * 100) + 1; } while (called.includes(n));
            called.push(n);
            let L = getLetter(n);
            
            document.getElementById('currentLetter').innerText = L;
            document.getElementById('currentNum').innerText = n;
            document.getElementById('historyBox').innerHTML += `<b>${L}-${n}</b>, `;

            if (selectedNumbers.includes(n)) {
                document.getElementById('winMsg').innerHTML = `🎊 BINGO! ${L}-${n} 🎊<br>MO'ATTEETTA!`;
                tg.MainButton.setText("MAALLAQA FUDHU").show();
            } else {
                setTimeout(nextCall, 4000);
            }
        }
    </script>
    </body>
    </html>
    """

# 3. BOT & SERVER
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Baga nagaan dhuftan! Tikeetii keessan xuxuxuun filadha.\nTimer: 1 Minute.", 
                     reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Filadhu", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/set_webhook")
def set_webhook():
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Webhook set successfully!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
