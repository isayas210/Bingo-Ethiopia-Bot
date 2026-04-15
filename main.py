import os
import time
import random
import telebot
from flask import Flask, request, render_template_string, jsonify
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# --- SERVER-SIDE GAME STATE ---
# Taphni kun server irratti namni hundaaf wal-qixa deema
game_state = {
    "start_time": time.time(),
    "called_numbers": [],
    "is_drawing": False,
    "last_ball": None
}

def update_game_logic():
    global game_state
    now = time.time()
    elapsed = now - game_state["start_time"]
    
    # Sekoondii 40f filannoo, sana booda lakkofsa 60 waamuuf (3s gidduutti)
    if elapsed < 40:
        game_state["is_drawing"] = False
        game_state["called_numbers"] = []
    else:
        game_state["is_drawing"] = True
        # Lakkofsa meeqa waamamu akka qabu (elapsed - 40) / 3sec
        needed_balls = int((elapsed - 40) // 3.5)
        if len(game_state["called_numbers"]) < needed_balls and len(game_state["called_numbers"]) < 75:
            while len(game_state["called_numbers"]) < needed_balls:
                n = random.randint(1, 100)
                if n not in game_state["called_numbers"]:
                    game_state["called_numbers"].append(n)
            game_state["last_ball"] = game_state["called_numbers"][-1]
            
    # Taphni tokko yoo xumurame (fakkeenyaaf sekoondii 300 booda) deebisii eegali
    if elapsed > 300:
        game_state = {"start_time": time.time(), "called_numbers": [], "is_drawing": False, "last_ball": None}

@app.route('/game_status')
def get_status():
    update_game_logic()
    now = time.time()
    return jsonify({
        "elapsed": now - game_state["start_time"],
        "called": game_state["called_numbers"],
        "is_drawing": game_state["is_drawing"],
        "last_ball": game_state["last_ball"]
    })

# --- HTML INTERFACE ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="or">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Bingo Live Ethiopia</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
        .container { background: #001f3f; border: 2px solid #00d4ff; border-radius: 20px; padding: 15px; max-width: 500px; margin: auto; }
        .grid-100 { display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 10px; }
        .n-btn { background: #1a2a44; border: 1px solid #007bff; color: white; padding: 10px 0; border-radius: 5px; font-size: 11px; }
        .n-btn.active { background: #ffcc00; color: #000; font-weight: bold; }
        .bingo-card { width: 100%; border-collapse: separate; border-spacing: 2px; margin-top: 15px; background: #000; border: 2px solid #ffcc00; }
        .bingo-card td { height: 40px; width: 20%; background: #1a2a44; border-radius: 4px; font-weight: bold; }
        .bingo-card td.marked { background: #28a745 !important; box-shadow: inset 0 0 8px #fff; }
        .ball { font-size: 50px; font-weight: bold; background: white; color: #001f3f; width: 90px; height: 90px; line-height: 90px; border-radius: 50%; border: 5px solid #ffcc00; display: inline-block; margin: 10px 0; }
        .timer { font-size: 20px; color: #ff4444; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <h2 style="color:#ffcc00;">BINGO LIVE 24/7</h2>
    
    <div id="selection-view">
        <div class="timer" id="timer-display">Eeggachaa...</div>
        <p style="font-size:12px;">Tikeetiwwan kee kuttachuuf lakkofsa cuqaasi (1-100):</p>
        <div class="grid-100" id="picker"></div>
        <p>Tikeetii: <span id="count" style="color:#ffcc00;">0</span></p>
    </div>

    <div id="game-view" style="display:none;">
        <div class="ball" id="ballNum">?</div>
        <div id="ticket-container"></div>
    </div>
</div>

<script>
    let selectedTickets = [];
    let myTicketsData = {};
    let isGameStarted = false;

    // Build Picker
    const picker = document.getElementById('picker');
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.className = 'n-btn'; b.innerText = i;
        b.onclick = () => {
            if(selectedTickets.includes(i)) {
                selectedTickets = selectedTickets.filter(x => x !== i); b.classList.remove('active');
            } else {
                selectedTickets.push(i); b.classList.add('active');
                generateTicketData(i);
            }
            document.getElementById('count').innerText = selectedTickets.length;
        };
        picker.appendChild(b);
    }

    function generateTicketData(id) {
        let nums = [];
        while(nums.length < 25) {
            let r = Math.floor(Math.random()*100)+1;
            if(!nums.includes(r)) nums.push(r);
        }
        myTicketsData[id] = nums;
    }

    async function sync() {
        let res = await fetch('/game_status');
        let data = await res.json();
        
        if (!data.is_drawing) {
            let remain = Math.max(0, 40 - Math.floor(data.elapsed));
            document.getElementById('timer-display').innerText = "Tikeetii Kuti: " + remain + "s";
            document.getElementById('selection-view').style.display = 'block';
            document.getElementById('game-view').style.display = 'none';
            isGameStarted = false;
        } else {
            if(!isGameStarted) {
                document.getElementById('selection-view').style.display = 'none';
                document.getElementById('game-view').style.display = 'block';
                renderMyTickets();
                isGameStarted = true;
            }
            document.getElementById('ballNum').innerText = data.last_ball || "?";
            // Mark all called numbers
            data.called.forEach(n => {
                selectedTickets.forEach(tId => {
                    let cell = document.getElementById(`t${tId}-n${n}`);
                    if(cell) cell.classList.add('marked');
                });
            });
        }
    }

    function renderMyTickets() {
        const cont = document.getElementById('ticket-container');
        cont.innerHTML = "";
        selectedTickets.forEach(tId => {
            let html = `<p>Tikeetii #${tId}</p><table class="bingo-card"><tbody>`;
            let nums = myTicketsData[tId];
            for(let r=0; r<5; r++) {
                html += "<tr>";
                for(let c=0; c<5; c++) {
                    let v = nums[r*5+c];
                    html += `<td id="t${tId}-n${v}">${v}</td>`;
                }
                html += "</tr>";
            }
            html += "</tbody></table>";
            let div = document.createElement('div'); div.innerHTML = html;
            cont.appendChild(div);
        });
    }

    setInterval(sync, 2000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Bingo Ethiopia Live! Taphni deemaa jira. Sekoondii 40 keessatti tikeetii kee filadhu.", 
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🎮 Bingo Bani", web_app=WebAppInfo(url=RENDER_URL))))

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
