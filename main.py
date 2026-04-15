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
        <title>Bingo Ethiopia 1-100</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; }
            
            /* Grid Filannoo 1-100 */
            .selection-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; max-height: 300px; overflow-y: auto; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; }
            .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 5px; cursor: pointer; }
            .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; }

            /* 5x5 Live Grid */
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin-top: 10px; }
            .cell { background: #1a2a44; height: 45px; line-height: 45px; border: 1px solid #333; border-radius: 5px; font-size: 14px; }
            .cell.marked { background: #28a745; color: white; font-weight: bold; }

            .timer-box { font-size: 20px; color: #ff4444; font-weight: bold; margin-bottom: 10px; }
            .num-circle { font-size: 50px; font-weight: bold; background: white; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; border: 4px solid #ffcc00; display: inline-block; margin: 15px 0; }
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; border: 2px solid #fff; margin-top: 15px; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00;">BINGO ETHIOPIA</h2>
        
        <div id="setup">
            <div class="timer-box">Hafe: <span id="timer">40</span>s</div>
            <p style="font-size:12px;">Lakkofsota 25 filadhu (1-100):</p>
            <div class="selection-grid" id="grid-100"></div>
            <p id="count" style="color:#00ffcc;">Filatame: 0/25</p>
        </div>

        <div id="game" style="display:none;">
            <div class="bingo-grid" id="live-grid"></div>
            <div class="num-circle" id="curN">?</div>
            <div class="win-msg" id="win-area">
                <h2 style="margin:0;">🎊 BINGO! 🎊</h2>
                <p>Lakkofsa Injifate: <span id="win-n" style="font-size:22px; font-weight:bold;"></span></p>
            </div>
            <div id="hist" style="font-size:12px; color:#aaa; margin-top:10px;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timer = 40;
        let selected = [];
        let called = [];
        let isGameOver = false;

        // 1-100 Grid uumuu
        const g100 = document.getElementById('grid-100');
        for(let i=1; i<=100; i++) {
            let b = document.createElement('button');
            b.className = 'n-btn'; b.innerText = i;
            b.onclick = () => {
                if(selected.includes(i)) {
                    selected = selected.filter(x => x !== i);
                    b.classList.remove('active');
                } else if(selected.length < 25) {
                    selected.push(i);
                    b.classList.add('active');
                }
                document.getElementById('count').innerText = "Filatame: " + selected.length + "/25";
            };
            g100.appendChild(b);
        }

        // Timer
        let cd = setInterval(() => {
            timer--;
            document.getElementById('timer').innerText = timer;
            if(timer <= 0) { clearInterval(cd); startGame(); }
        }, 1000);

        function startGame() {
            // Yoo namni sun homaa hin filatin, ofumaan 25 guuti
            while(selected.length < 25) {
                let r = Math.floor(Math.random()*100)+1;
                if(!selected.includes(r)) selected.push(r);
            }
            
            document.getElementById('setup').style.display = 'none';
            document.getElementById('game').style.display = 'block';
            
            // 5x5 Grid uumuu
            const lg = document.getElementById('live-grid');
            selected.forEach(n => {
                let d = document.createElement('div');
                d.className = 'cell'; d.id = 'c-' + n; d.innerText = n;
                lg.appendChild(d);
            });
            
            runBingo();
        }

        function runBingo() {
            if(called.length >= 100 || isGameOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            
            document.getElementById('curN').innerText = n;
            document.getElementById('hist').innerHTML += n + ", ";

            let cell = document.getElementById('c-' + n);
            if(cell) {
                cell.classList.add('marked');
                // Line 1 Win Logic
                isGameOver = true;
                document.getElementById('win-area').style.display = 'block';
                document.getElementById('win-n').innerText = n;
                tg.MainButton.setText("INJIFATTEETTA!").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(runBingo, 3500);
            }
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Lakkofsa 1-100 gidduu jiru filachuuf sekondii 40 qabdu.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
