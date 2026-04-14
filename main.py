import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. MINI APP INTERFACE (B-I-N-G-O Style)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia - BINGO Style</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #001f3f; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: #003366; padding: 15px; border-radius: 15px; border: 1px solid #00d4ff; }
            h1 { color: #ffcc00; font-size: 24px; letter-spacing: 5px; }
            .wallet { font-size: 14px; color: #00ffcc; margin-bottom: 10px; }
            input { padding: 10px; width: 80%; border-radius: 5px; border: none; margin: 10px 0; }
            .btn { background: #28a745; color: white; padding: 12px; border: none; border-radius: 8px; width: 90%; font-weight: bold; }
            
            /* BINGO Call Style */
            .call-display { margin: 20px 0; }
            .letter { font-size: 30px; font-weight: bold; color: #ffcc00; display: block; }
            .number { font-size: 60px; font-weight: bold; background: #fff; color: #003366; padding: 10px 25px; border-radius: 10px; display: inline-block; box-shadow: 0 0 15px #ffcc00; }
            
            .history-box { background: #001a33; padding: 10px; border-radius: 8px; height: 100px; overflow-y: auto; font-size: 14px; text-align: left; margin-top: 15px; }
            .win-animation { color: #2ecc71; font-size: 20px; font-weight: bold; margin-top: 15px; animation: blink 1s infinite; }
            @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>

    <div class="card">
        <h1>B-I-N-G-O</h1>
        <div class="wallet">CBE: 1000659750973 | Balance: 0.00</div>

        <div id="setup-area">
            <p>Gatii Tikeetii (5-100):</p>
            <input type="number" id="price" value="5" min="5">
            <p>Lakk. Tikeetii Kee (Hanga 10):</p>
            <input type="text" id="tickets" placeholder="Fkn: 12, 45, 6">
            <button class="btn" onclick="startBingo()">TAPHA JALQABI</button>
        </div>

        <div id="game-area" style="display:none;">
            <div class="call-display">
                <span class="letter" id="currentLetter">WAITING...</span>
                <span class="number" id="currentNum">?</span>
            </div>
            <p>Tikeetota Kee: <span id="myTickets" style="color:#00ffcc;"></span></p>
            <div class="history-box" id="history">History: </div>
            <div id="winMsg"></div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let called = [];
        let myTickets = [];
        let bet = 5;

        function getLetter(n) {
            if (n <= 20) return "B";
            if (n <= 40) return "I";
            if (n <= 60) return "N";
            if (n <= 80) return "G";
            return "O";
        }

        function startBingo() {
            let tInput = document.getElementById('tickets').value;
            bet = parseInt(document.getElementById('price').value);
            myTickets = tInput.split(',').map(x => parseInt(x.trim())).filter(x => x > 0);
            
            if (myTickets.length == 0) return alert("Tikeetii galchi!");
            
            document.getElementById('setup-area').style.display = 'none';
            document.getElementById('game-area').style.display = 'block';
            document.getElementById('myTickets').innerText = myTickets.join(', ');
            
            nextCall();
        }

        function nextCall() {
            if (called.length >= 100) return;
            let n;
            do { n = Math.floor(Math.random() * 100) + 1; } while (called.includes(n));
            
            called.push(n);
            let L = getLetter(n);
            
            document.getElementById('currentLetter').innerText = L;
            document.getElementById('currentNum').innerText = n;
            document.getElementById('history').innerHTML += `<b>${L}-${n}</b>, `;

            if (myTickets.includes(n)) {
                let win = (bet * myTickets.length) * 0.70;
                document.getElementById('winMsg').innerHTML = `<div class="win-animation">🎊 BINGO! ${L}-${n} 🎊<br>MO'ATTEETTA: ${win.toFixed(2)} ETB</div>`;
                tg.MainButton.setText("MAALLAQA FUDHU").show();
            } else {
                setTimeout(nextCall, 4000);
            }
        }
    </script>
    </body>
    </html>
    """

# 3. BOT & WEBHOOK (Akkuma duraatti itti fufa)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Baga nagaan dhuftan! Bingo Ethiopia B-I-N-G-O style qindaa'eera.", 
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
