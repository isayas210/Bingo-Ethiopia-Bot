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
        <title>Bingo Ethiopia - Multi Ticket</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
            .card { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 10px; margin-bottom: 15px; }
            
            /* Multi-Ticket Layout */
            #ticket-container { display: flex; flex-direction: column; gap: 20px; align-items: center; }
            .bingo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; background: #000; padding: 5px; border-radius: 8px; width: 280px; border: 1px solid #555; }
            .bingo-header { background: #ffcc00; color: #000; font-weight: bold; font-size: 14px; padding: 5px 0; }
            .cell { background: #1a2a44; height: 35px; line-height: 35px; font-size: 13px; border: 1px solid #333; }
            .cell.marked { background: #28a745; color: white; box-shadow: inset 0 0 5px #fff; }

            .controls { margin-bottom: 20px; }
            .btn-select { background: #007bff; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; font-weight: bold; }
            .btn-select.active { background: #ffcc00; color: #000; }
            
            .ball { font-size: 50px; font-weight: bold; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; border: 4px solid #ffcc00; display: inline-block; margin: 15px 0; }
            .win-msg { display: none; background: #28a745; padding: 15px; border-radius: 10px; margin-top: 10px; border: 2px solid #fff; }
        </style>
    </head>
    <body>
    <div class="card">
        <h2 style="color:#ffcc00; margin:5px;">BINGO ETHIOPIA</h2>
        
        <div id="setup">
            <p>Tikeetii meeqa kuttu?</p>
            <div class="controls">
                <button class="btn-select" onclick="setTickets(5)" id="btn5">5 TIKEETII</button>
                <button class="btn-select" onclick="setTickets(10)" id="btn10">10 TIKEETII</button>
            </div>
            <p class="timer">Hafe: <span id="timer">40</span>s</p>
            <div id="preview-msg" style="font-size:12px; color:#00ffcc;">Ofumaan siif filatama...</div>
        </div>

        <div id="game" style="display:none;">
            <div class="ball" id="curN">?</div>
            <div class="win-msg" id="win-area">
                <h1 style="margin:0;">🎊 BINGO! 🎊</h1>
                <p>Tikeetii kee keessaa tokko sarara 1 guuteera!</p>
            </div>
            <div id="ticket-container"></div>
            <div id="hist" style="font-size:11px; color:#aaa; margin-top:15px;">History: </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        let timer = 40;
        let numTickets = 5; // Default
        let allTickets = [];
        let called = [];
        let isGameOver = false;

        function setTickets(n) {
            numTickets = n;
            document.getElementById('btn5').classList.toggle('active', n===5);
            document.getElementById('btn10').classList.toggle('active', n===10);
        }

        let cd = setInterval(() => {
            timer--;
            document.getElementById('timer').innerText = timer;
            if(timer <= 0) { clearInterval(cd); startGame(); }
        }, 1000);

        function generateTicket() {
            let tix = [];
            while(tix.length < 25) {
                let r = Math.floor(Math.random()*100)+1;
                if(!tix.includes(r)) tix.push(r);
            }
            return tix;
        }

        function startGame() {
            document.getElementById('setup').style.display = 'none';
            document.getElementById('game').style.display = 'block';
            
            const container = document.getElementById('ticket-container');
            for(let i=0; i<numTickets; i++) {
                let tixData = generateTicket();
                allTickets.push(tixData);
                
                let grid = document.createElement('div');
                grid.className = 'bingo-grid';
                grid.innerHTML = '<div class="bingo-header">B</div><div class="bingo-header">I</div><div class="bingo-header">N</div><div class="bingo-header">G</div><div class="bingo-header">O</div>';
                
                tixData.forEach(n => {
                    let d = document.createElement('div');
                    d.className = 'cell';
                    d.id = `tix${i}-n${n}`;
                    d.innerText = n;
                    grid.appendChild(d);
                });
                
                let title = document.createElement('p');
                title.innerText = "Tikeetii #" + (i+1);
                title.style.margin = "5px 0";
                container.appendChild(title);
                container.appendChild(grid);
            }
            play();
        }

        function play() {
            if(called.length >= 100 || isGameOver) return;
            let n; do { n = Math.floor(Math.random()*100)+1; } while(called.includes(n));
            called.push(n);
            
            document.getElementById('curN').innerText = n;
            document.getElementById('hist').innerHTML += n + ", ";

            // Tikeetota hunda keessatti lakkofsa kana barbaadi
            for(let i=0; i<numTickets; i++) {
                let cell = document.getElementById(`tix${i}-n${n}`);
                if(cell) {
                    cell.classList.add('marked');
                    checkLineWin(i);
                }
            }

            if(!isGameOver) setTimeout(play, 3500);
        }

        function checkLineWin(tixIndex) {
            // Logic salphaa: Tikeetii tokko keessaa 5 yoo guute (Line 1)
            let markedCount = document.querySelectorAll(`#ticket-container .bingo-grid:nth-of-type(${tixIndex+1}) .cell.marked`).length;
            
            // Asirratti 'Line 1' jechuun sarara tokko guutuu dha.
            // Fakkeenyaaf, yoo xiqqaate lakkofsota 5 tikeetii tokko keessaa yoo guutan:
            if(markedCount >= 5) {
                isGameOver = true;
                document.getElementById('win-area').style.display = 'block';
                tg.MainButton.setText("INJIFATTEETTA! - FUDHU").show();
                tg.HapticFeedback.notificationOccurred('success');
            }
        }
    </script>
    </body>
    </html>
    """

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Baga nagaan dhuftan! Tikeetii 5 ykn 10 filadhu.\n40 sec booda taphni ofumaan eegala.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
