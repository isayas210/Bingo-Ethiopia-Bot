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
        <title>Bingo Ethiopia - Logic Master</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 15px; box-shadow: 0 0 20px #00d4ff; }
            
            /* Picker 1-100 */
            .grid-100 { display: grid; grid-template-columns: repeat(10, 1fr); gap: 3px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 8px; border: 1px solid #333; }
            .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 4px; font-size: 10px; cursor: pointer; }
            .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; }

            /* Bingo Grid 5x5 */
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin-top: 20px; background: #000; padding: 10px; border-radius: 10px; }
            .cell { background: #1a2a44; height: 50px; line-height: 50px; font-size: 16px; font-weight: bold; border-radius: 5px; border: 1px solid #333; transition: 0.3s; }
            .cell.marked { background: #28a745; color: white; box-shadow: inset 0 0 10px #fff; border-color: #fff; }

            .ball-ui { font-size: 55px; font-weight: bold; background: white; color: #001f3f; width: 100px; height: 100px; line-height: 100px; border-radius: 50%; border: 5px solid #ffcc00; display: inline-block; margin: 15px 0; }
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; border: 3px solid #fff; margin-bottom: 15px; }
            .timer { font-size: 20px; color: #ff4444; font-weight: bold; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA</h2>
        
        <div id="selection-stage">
            <div class="timer">Hafe: <span id="time-left">40</span>s</div>
            <p style="font-size:12px;">Lakkofsota 25 filadhu (1-100):</p>
            <div class="grid-100" id="picker-grid"></div>
            <p id="sel-stat" style="margin-top:10px;">Filatame: 0/25</p>
            <button onclick="startGame()" style="background:#28a745; color:white; border:none; padding:12px; width:100%; border-radius:8px; font-weight:bold;">TAPHA JALQABI</button>
        </div>

        <div id="game-stage" style="display:none;">
            <div class="ball-ui" id="curBall">?</div>
            <div class="win-msg" id="winArea">
                <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
                <p>SARARRI GUUTAMEERA!</p>
            </div>
            <div class="bingo-grid" id="main-grid"></div>
            <div id="history" style="font-size:11px; color:#aaa; margin-top:15px; text-align:left;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timeLeft = 40;
        let selected = [];
        let called = [];
        let isGameOver = false;

        // Grid 1-100
        const picker = document.getElementById('picker-grid');
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
                document.getElementById('sel-stat').innerText = "Filatame: " + selected.length + "/25";
            };
            picker.appendChild(b);
        }

        let cd = setInterval(() => {
            timeLeft--;
            document.getElementById('time-left').innerText = timeLeft;
            if(timeLeft <= 0) { clearInterval(cd); startGame(); }
        }, 1000);

        function startGame() {
            clearInterval(cd);
            while(selected.length < 25) {
                let r = Math.floor(Math.random()*100)+1;
                if(!selected.includes(r)) selected.push(r);
            }
            document.getElementById('selection-stage').style.display = 'none';
            document.getElementById('game-stage').style.display = 'block';
            
            const grid = document.getElementById('main-grid');
            selected.forEach((n, i) => {
                let d = document.createElement('div');
                d.className = 'cell'; d.id = 'cell-' + n; d.innerText = n;
                // Index hordofuuf attribute itti dibna
                d.setAttribute('data-index', i);
                grid.appendChild(d);
            });
            draw();
        }

        function draw() {
            if(called.length >= 100 || isGameOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            
            document.getElementById('curBall').innerText = n;
            document.getElementById('history').innerHTML += n + ", ";

            let match = document.getElementById('cell-' + n);
            if(match) {
                match.classList.add('marked');
                checkBingo();
            }
            if(!isGameOver) setTimeout(draw, 3500);
        }

        function checkBingo() {
            const cells = document.querySelectorAll('.cell');
            let board = [];
            cells.forEach(c => board.push(c.classList.contains('marked')));

            // Logic Horizontal (Dalgee)
            for (let i = 0; i < 25; i += 5) {
                if (board[i] && board[i+1] && board[i+2] && board[i+3] && board[i+4]) win();
            }

            // Logic Vertical (Ol-gadii)
            for (let i = 0; i < 5; i++) {
                if (board[i] && board[i+5] && board[i+10] && board[i+15] && board[i+20]) win();
            }
        }

        function win() {
            if(isGameOver) return;
            isGameOver = true;
            document.getElementById('winArea').style.display = 'block';
            tg.MainButton.setText("BINGO! - FUDHU").show();
            tg.HapticFeedback.notificationOccurred('success');
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Lakkofsa 25 filadhu. Mo'achuuf sarara tokko (Horizontal ykn Vertical) guutuu cufuu qabda.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
