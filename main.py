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
        <title>Bingo Ethiopia - Selection First</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 15px #00d4ff; }
            h2 { color: #ffcc00; margin-top: 0; }
            
            /* Selection Grid */
            .grid-100 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; max-height: 350px; overflow-y: auto; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 10px; border: 1px solid #333; }
            .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 12px 0; border-radius: 6px; cursor: pointer; font-size: 14px; }
            .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; border-color: #fff; transform: scale(0.95); }

            /* Live Game Grid */
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 15px; }
            .cell { background: #1a2a44; height: 50px; line-height: 50px; border: 1px solid #333; border-radius: 5px; font-weight: bold; }
            .cell.marked { background: #28a745; color: white; border: 2px solid #fff; box-shadow: 0 0 10px #28a745; }

            .timer { font-size: 20px; color: #ff4444; font-weight: bold; margin-bottom: 10px; }
            .ball { font-size: 60px; font-weight: bold; background: white; color: #001f3f; width: 110px; height: 110px; line-height: 110px; border-radius: 50%; border: 5px solid #ffcc00; display: inline-block; margin: 20px 0; }
            .win-box { display: none; background: #28a745; padding: 20px; border-radius: 15px; border: 3px solid #fff; margin-top: 15px; }
            button#start-now { background: #28a745; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2>BINGO ETHIOPIA</h2>
        
        <div id="selection-stage">
            <div class="timer">Yeroo: <span id="time">40</span>s</div>
            <p style="font-size:14px; color:#00ffcc;">Lakkofsota 25 filadhu (1-100):</p>
            <div class="grid-100" id="picker"></div>
            <p id="stat">Filatame: 0/25</p>
            <button id="start-now" onclick="confirmSelection()">TAPHA JALQABI</button>
        </div>

        <div id="game-stage" style="display:none;">
            <div class="bingo-grid" id="main-grid"></div>
            <div class="ball" id="currentNum">?</div>
            <div class="win-box" id="win-ui">
                <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
                <p>Injifate: <span id="winner-n" style="font-size:30px;"></span></p>
            </div>
            <div id="logs" style="font-size:12px; color:#aaa; margin-top:10px; text-align:left; height:50px; overflow:auto;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timeLeft = 40;
        let selected = [];
        let called = [];
        let isOver = false;

        // 1-100 Grid uumuu
        const picker = document.getElementById('picker');
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
                document.getElementById('stat').innerText = "Filatame: " + selected.length + "/25";
            };
            picker.appendChild(b);
        }

        // Timer
        let timerId = setInterval(() => {
            timeLeft--;
            document.getElementById('time').innerText = timeLeft;
            if(timeLeft <= 0) { clearInterval(timerId); confirmSelection(); }
        }, 1000);

        function confirmSelection() {
            clearInterval(timerId);
            // Yoo gahaa hin filatin ofumaan guuti
            while(selected.length < 25) {
                let r = Math.floor(Math.random()*100)+1;
                if(!selected.includes(r)) selected.push(r);
            }
            
            document.getElementById('selection-stage').style.display = 'none';
            document.getElementById('game-stage').style.display = 'block';
            
            // 5x5 Live Grid uumuu
            const mg = document.getElementById('main-grid');
            selected.sort((a,b) => a-b).forEach(n => {
                let d = document.createElement('div');
                d.className = 'cell'; d.id = 'cell-' + n; d.innerText = n;
                mg.appendChild(d);
            });
            
            setTimeout(drawBall, 2000);
        }

        function drawBall() {
            if(called.length >= 100 || isOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            
            document.getElementById('currentNum').innerText = n;
            document.getElementById('logs').innerHTML += n + ", ";

            let match = document.getElementById('cell-' + n);
            if(match) {
                match.classList.add('marked');
                // Line 1 Win Logic: Inni jalqaba karteellaa isaa irratti lakkofsa argate ni mo'ata
                isOver = true;
                document.getElementById('win-ui').style.display = 'block';
                document.getElementById('winner-n').innerText = n;
                tg.MainButton.setText("MAALLAQA FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                setTimeout(drawBall, 3000);
            }
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Lakkofsa 1-100 gidduu jiru filachuun tapha jalqabaa.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
