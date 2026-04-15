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

# --- SYSTEM LOGIC ---
# Tikeetii 100 qopheessina (100 keessaa namni kute ni galmaa'a, kan hafe 'Mana')
game_data = {
    "start_time": time.time(),
    "called_balls": [],
    "tickets": {}, # {ticket_id: [numbers]}
    "winners": [],
    "is_active": False
}

def setup_new_game():
    global game_data
    game_data["start_time"] = time.time()
    game_data["called_balls"] = []
    game_data["winners"] = []
    game_data["is_active"] = False
    # Tikeetii 100 guutuu lakkofsa random uumnaan
    for i in range(1, 101):
        nums = random.sample(range(1, 101), 25)
        game_data["tickets"][i] = nums

setup_new_game()

@app.route('/game_sync')
def game_sync():
    now = time.time()
    elapsed = now - game_data["start_time"]
    
    # 40s Selection, booda drawing eegala
    if elapsed > 40:
        game_data["is_active"] = True
        needed_balls = int((elapsed - 40) // 3) # 3 sec tokko
        if len(game_data["called_balls"]) < needed_balls and len(game_data["called_balls"]) < 100:
            while len(game_data["called_balls"]) < needed_balls:
                n = random.randint(1, 100)
                if n not in game_data["called_balls"]:
                    game_data["called_balls"].append(n)
        
    return jsonify({
        "elapsed": elapsed,
        "called": game_data["called_balls"],
        "is_active": game_data["is_active"],
        "tickets": game_data["tickets"] # Tikeetii 100nuu ni erga
    })

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="or">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Bingo Ethiopia - House System</title>
    <style>
        body { font-family: sans-serif; background: #050a14; color: white; text-align: center; margin: 0; padding: 10px; }
        .card-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 20px; }
        .bingo-table { font-size: 10px; border-collapse: collapse; width: 100%; background: #000; border: 1px solid #ffcc00; }
        .bingo-table td { border: 1px solid #333; height: 25px; text-align: center; }
        .marked { background: #28a745 !important; color: white; }
        .house-label { font-size: 9px; color: #ff4444; }
        .user-label { font-size: 9px; color: #00ffcc; font-weight: bold; }
        .ball { font-size: 40px; background: white; color: #000; width: 80px; height: 80px; border-radius: 50%; line-height: 80px; display: inline-block; border: 4px solid #ffcc00; }
    </style>
</head>
<body>
    <h2 style="color:#ffcc00;">BINGO ETHIOPIA LIVE</h2>
    <div id="status">Eeggachaa...</div>
    <div class="ball" id="currentBall">?</div>
    
    <div id="selection-zone">
        <h3>Tikeetii Kee Kuti (1-100)</h3>
        <div id="picker-grid" style="display:grid; grid-template-columns: repeat(10, 1fr); gap:2px;"></div>
    </div>

    <div id="game-zone" style="display:none;">
        <div class="card-container" id="all-cards"></div>
    </div>

<script>
    let myTickets = [];
    let allTicketsData = {};
    let isWinnerFound = false;

    // 1. Grid Picker
    const picker = document.getElementById('picker-grid');
    for(let i=1; i<=100; i++) {
        let b = document.createElement('button');
        b.innerText = i;
        b.style.padding = "5px";
        b.onclick = () => {
            if(!myTickets.includes(i)) {
                myTickets.push(i);
                b.style.background = "#ffcc00";
            }
        };
        picker.appendChild(b);
    }

    async function sync() {
        if(isWinnerFound) return;
        let res = await fetch('/game_sync');
        let data = await res.json();
        allTicketsData = data.tickets;

        if(data.is_active) {
            document.getElementById('selection-zone').style.display = 'none';
            document.getElementById('game-zone').style.display = 'block';
            document.getElementById('currentBall').innerText = data.called[data.called.length-1] || "?";
            renderCards(data.called);
        } else {
            document.getElementById('status').innerText = "Tikeetii Kuti: " + Math.max(0, 40 - Math.floor(data.elapsed)) + "s";
        }
    }

    function renderCards(called) {
        const container = document.getElementById('all-cards');
        container.innerHTML = "";
        
        for(let i=1; i<=100; i++) {
            let nums = allTicketsData[i];
            let isMine = myTickets.includes(i);
            let table = `<div class="card-box">
                <span class="${isMine ? 'user-label' : 'house-label'}">${isMine ? 'TIKEETII KEE' : 'TIKEETII MANAA'} #${i}</span>
                <table class="bingo-table">`;
            
            let markedCountInTicket = 0;
            for(let r=0; r<5; r++) {
                table += "<tr>";
                let rowMarked = 0;
                for(let c=0; c<5; c++) {
                    let v = nums[r*5+c];
                    let isMarked = called.includes(v);
                    if(isMarked) rowMarked++;
                    table += `<td class="${isMarked ? 'marked' : ''}">${v}</td>`;
                }
                table += "</tr>";
                if(rowMarked === 5) announceBingo(i, isMine);
            }
            table += "</table></div>";
            container.innerHTML += table;
        }
    }

    function announceBingo(id, isMine) {
        if(isWinnerFound) return;
        isWinnerFound = true;
        let winner = isMine ? "ATTI INJIFATTEETTA! (x100)" : "MANNI MO'ATE! (Taphattoonni hundi kishiraniiru)";
        alert("BINGO! Tikeetii #" + id + "\\n" + winner);
        setTimeout(() => location.reload(), 5000);
    }

    setInterval(sync, 2000);
</script>
</body>
</html>
