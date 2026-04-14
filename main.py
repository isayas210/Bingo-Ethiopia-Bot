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
        <title>Bingo Ethiopia - Line 1 Master</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #050a14; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 20px; padding: 15px; box-shadow: 0 0 20px #00d4ff; }
            h1 { color: #ffcc00; font-size: 24px; margin-bottom: 10px; }
            
            /* Bingo Table Style */
            .bingo-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
            .bingo-table th { background: #ffcc00; color: #000; padding: 10px; font-size: 18px; }
            .bingo-table td { border: 1px solid #007bff; height: 40px; font-size: 14px; background: #1a2a44; }
            .bingo-table td.marked { background: #28a745; color: white; font-weight: bold; }

            .call-circle { font-size: 50px; font-weight: bold; background: white; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; margin: 10px; }
            
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; border: 2px solid #fff; margin-top: 15px; font-weight: bold; }
            .history { background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; height: 60px; overflow-y: auto; font-size: 12px; margin-top: 10px; }
        </style>
    </head>
    <body>
    <div class="card">
        <h1>BINGO ETHIOPIA</h1>
        
        <div id="game-area">
            <table class="bingo-table">
                <tr>
                    <th>B</th><th>I</th><th>N</th><th>G</th><th>O</th>
                </tr>
                <tr>
                    <td id="cell-B"></td><td id="cell-I"></td><td id="cell-N"></td><td id="cell-G"></td><td id="cell-O"></td>
                </tr>
            </table>

            <div id="call-box">
                <span id="curL" style="font-size: 20px; color: #ffcc00; display: block;">EGGATTU...</span>
                <div class="call-circle" id="curN">?</div>
            </div>

            <div class="win-msg" id="win-area">
                🎊 BINGO! LINE 1 CUFAME 🎊<br>
                INJIFATE: <span id="win-num"></span>
            </div>

            <div class="history" id="hist">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let called = [];
        let isGameOver = false;

        // Tikeetii tokkoof karteellaa Bingo 1 (Randomly generated for the user)
        let myTicket = {
            'B': Math.floor(Math.random() * 20) + 1,
            'I': Math.floor(Math.random() * 20) + 21,
            'N': Math.floor(Math.random() * 20) + 41,
            'G': Math.floor(Math.random() * 20) + 61,
            'O': Math.floor(Math.random() * 20) + 81
        };

        // UI irratti karteellaa guutuu
        document.getElementById('cell-B').innerText = myTicket['B'];
        document.getElementById('cell-I').innerText = myTicket['I'];
        document.getElementById('cell-N').innerText = myTicket['N'];
        document.getElementById('cell-G').innerText = myTicket['G'];
        document.getElementById('cell-O').innerText = myTicket['O'];

        let hits = 0;

        function nextBall() {
            if(called.length >= 100 || isGameOver) return;
            
            let n; 
            do { n = Math.floor(Math.random() * 100) + 1; } while(called.includes(n));
            called.push(n);
            
            let L = n<=20?'B':n<=40?'I':n<=60?'N':n<=80?'G':'O';
            document.getElementById('curL').innerText = L;
            document.getElementById('curN').innerText = n;
            document.getElementById('hist').innerHTML += L + "-" + n + ", ";

            // Check if it matches user ticket
            Object.keys(myTicket).forEach(key => {
                if(myTicket[key] === n) {
                    document.getElementById('cell-' + key).classList.add('marked');
                    hits++;
                }
            });

            // Line 1 Win Logic (Namni dura sarara tokko guute)
            if(hits >= 1 && !isGameOver) {
                isGameOver = true;
                document.getElementById('win-area').style.display = 'block';
                document.getElementById('win-num').innerText = L + "-" + n;
                tg.MainButton.setText("MAALLAQA FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(nextBall, 4000);
            }
        }

        // Ofumaan jalqaba
        setTimeout(nextBall, 2000);
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Tikeetiin keessan qophiidha. Sarara 1 (Line 1) dura kan guute ni mo'ata.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
