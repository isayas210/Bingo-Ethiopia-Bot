import os
import telebot
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
        <title>Bingo Ethiopia 5x5</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 10px; box-shadow: 0 0 15px #00d4ff; }
            
            /* Bingo Grid 5x5 */
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin: 10px 0; background: #000; padding: 5px; border-radius: 8px; }
            .bingo-header { background: #ffcc00; color: #000; font-weight: bold; padding: 10px 0; font-size: 18px; }
            .cell { background: #1a2a44; height: 50px; line-height: 50px; font-size: 16px; border-radius: 4px; border: 1px solid #333; }
            .cell.marked { background: #28a745; color: white; font-weight: bold; box-shadow: inset 0 0 10px #fff; }

            .call-area { margin: 15px 0; }
            .num-circle { font-size: 50px; font-weight: bold; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; display: inline-block; border: 4px solid #ffcc00; }
            .timer-box { font-size: 18px; color: #ff4444; margin-bottom: 5px; }
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; border: 2px solid #fff; margin-top: 10px; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA</h2>
        
        <div id="setup">
            <div class="timer-box">Eeggattu: <span id="timer">40</span>s</div>
            <div class="bingo-grid" id="preview-grid">
                <div class="bingo-header">B</div><div class="bingo-header">I</div><div class="bingo-header">N</div><div class="bingo-header">G</div><div class="bingo-header">O</div>
            </div>
            <p style="font-size:12px; color:#00ffcc;">Karteellaan 5x5 ofumaan qophaa'eera.</p>
        </div>

        <div id="game" style="display:none;">
            <div class="bingo-grid" id="live-grid">
                <div class="bingo-header">B</div><div class="bingo-header">I</div><div class="bingo-header">N</div><div class="bingo-header">G</div><div class="bingo-header">O</div>
            </div>
            <div class="call-area">
                <div class="num-circle" id="curN">?</div>
            </div>
            <div class="win-msg" id="win-area">
                <h2 style="margin:0;">🎊 BINGO! 🎊</h2>
                <p>Sararri 1 Cufameera!</p>
            </div>
            <div id="hist" style="font-size:12px; color:#aaa; height:40px; overflow:auto;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timer = 40;
        let called = [];
        let isGameOver = false;

        // Tikeetii 5x5 uumuu (1-100 gidduu)
        function generateTicket() {
            let tix = [];
            for(let i=0; i<25; i++) {
                let n; do { n = Math.floor(Math.random()*100)+1; } while(tix.includes(n));
                tix.push(n);
            }
            return tix;
        }
        let myTicket = generateTicket();

        // Grid irratti fe'uu
        function fillGrids(id) {
            const g = document.getElementById(id);
            myTicket.forEach((n, index) => {
                let d = document.createElement('div');
                d.className = 'cell';
                d.id = id + '-' + n;
                d.innerText = n;
                g.appendChild(d);
            });
        }
        fillGrids('preview-grid');
        fillGrids('live-grid');

        // Timer
        let cd = setInterval(() => {
            timer--;
            document.getElementById('timer').innerText = timer;
            if(timer <= 0) { clearInterval(cd); startGame(); }
        }, 1000);

        function startGame() {
            document.getElementById('setup').style.display = 'none';
            document.getElementById('game').style.display = 'block';
            play();
        }

        function play() {
            if(called.length >= 100 || isGameOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            
            document.getElementById('curN').innerText = n;
            document.getElementById('hist').innerHTML += n + ", ";

            // Match check
            let cell = document.getElementById('live-grid-' + n);
            if(cell) {
                cell.classList.add('marked');
                checkWin();
            }

            if(!isGameOver) setTimeout(play, 3500);
        }

        function checkWin() {
            // Sarara 1 guutee yoo jiraate (Logic salphaa: 'marked' count)
            let markedCells = document.querySelectorAll('#live-grid .cell.marked').length;
            if(markedCells >= 5) { // Sarara 1 jechuun yoo xiqqaate 5 guutuu
                isGameOver = true;
                document.getElementById('win-area').style.display = 'block';
                tg.MainButton.setText("INJIFATTEETTA - MAALLAQA FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            }
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Karteellaa 5x5 qophaa'eera.\n40 sec booda ofumaan eegala.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
