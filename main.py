import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. MINI APP INTERFACE (Bingo v2.0)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia - Blues Coffee</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #001f3f; color: white; text-align: center; padding: 10px; margin: 0; }
            .card { background: #003366; padding: 15px; border-radius: 15px; border: 1px solid #00d4ff; margin-bottom: 10px; }
            h1 { color: #ffcc00; font-size: 20px; margin: 5px; }
            .section { display: none; }
            .active { display: block; }
            input, select { padding: 10px; width: 85%; border-radius: 5px; border: none; margin: 10px 0; font-size: 16px; }
            .btn { background: #28a745; color: white; padding: 12px; border: none; border-radius: 8px; width: 90%; font-weight: bold; cursor: pointer; }
            .btn-deposit { background: #ffcc00; color: #000; }
            .called-number { font-size: 45px; color: #ffcc00; font-weight: bold; background: #002b55; padding: 15px; border-radius: 50%; width: 70px; height: 70px; line-height: 70px; margin: 15px auto; border: 3px solid #ffcc00; }
            .ticket-box { background: #004080; padding: 5px; margin: 5px; border-radius: 5px; display: inline-block; min-width: 40px; }
        </style>
    </head>
    <body>

    <div class="card">
        <h1>Bingo Ethiopia</h1>
        
        <div id="deposit-section" class="section active">
            <p>Wallet: <span id="balance">0.00</span> ETB</p>
            <div style="text-align: left; font-size: 13px; background: #001a33; padding: 10px; border-radius: 8px;">
                CBE: 1000659750973 <br>
                Tele: 0974085753 <br>
                CBE Birr: 0974085753
            </div>
            <p>Screenshot kaffaltii fe'i:</p>
            <input type="file" id="screenshot" accept="image/*">
            <button class="btn btn-deposit" onclick="alert('Screenshot fe'ameera! Admin ni mirkaneessa.')">Kaffaltii Ergi</button>
            <hr>
            <button class="btn" onclick="showPlay()">Gara Taphaatti Darbi</button>
        </div>

        <div id="play-section" class="section">
            <p>Gatii Tikeetii (5 - 100 ETB):</p>
            <input type="number" id="ticketPrice" min="5" max="100" value="5">
            <p>Lakkofsa Tikeetii (Hanga 10 filachuu dandeessa, addaan fageessi):</p>
            <input type="text" id="ticketsInput" placeholder="Fkn: 5, 12, 45, 88">
            <button class="btn" onclick="startBingo()">🎟️ Tikeetii Kutadhu</button>
        </div>

        <div id="bingo-section" class="section">
            <p>Tikeetota Kee:</p>
            <div id="myTicketsList"></div>
            <div class="called-number" id="currentNum">?</div>
            <p>Lakkofsota dhufran: <span id="history" style="font-size:12px; color:#aaa;"></span></p>
            <div id="winMsg" style="color:#2ecc71; font-weight:bold;"></div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();

        let calledNumbers = [];
        let myTickets = [];
        let pricePerTicket = 5;

        function showPlay() {
            document.getElementById('deposit-section').classList.remove('active');
            document.getElementById('play-section').classList.add('active');
        }

        function startBingo() {
            let input = document.getElementById('ticketsInput').value;
            pricePerTicket = parseInt(document.getElementById('ticketPrice').value);
            
            if (pricePerTicket < 5 || pricePerTicket > 100) {
                alert("Gatiin tikeetii 5 hanga 100 qofa!"); return;
            }

            myTickets = input.split(',').map(n => parseInt(n.trim())).filter(n => n >= 1 && n <= 100);
            
            if (myTickets.length === 0 || myTickets.length > 10) {
                alert("Tikeetii 1 hanga 10 qofa filachuu dandeessa!"); return;
            }

            document.getElementById('play-section').classList.remove('active');
            document.getElementById('bingo-section').classList.add('active');
            
            let listHtml = "";
            myTickets.forEach(t => { listHtml += `<span class="ticket-box">${t}</span>`; });
            document.getElementById('myTicketsList').innerHTML = listHtml;
            
            nextNumber();
        }

        function nextNumber() {
            if (calledNumbers.length >= 100) return;
            let num;
            do { num = Math.floor(Math.random() * 100) + 1; } while (calledNumbers.includes(num));
            calledNumbers.push(num);
            document.getElementById('currentNum').innerText = num;
            document.getElementById('history').innerText = calledNumbers.join(', ');

            if (myTickets.includes(num)) {
                let totalBet = pricePerTicket * myTickets.length;
                let winAmount = totalBet * 0.70; // 70% win
                document.getElementById('winMsg').innerHTML = `🎊 BINGO! Tikeetii ${num} irratti mo'atteetta!<br>Gatii Win: ${winAmount.toFixed(2)} ETB`;
                tg.MainButton.setText("MAALLAQA FUDHU").show();
            } else {
                setTimeout(nextNumber, 3000);
            }
        }
    </script>
    </body>
    </html>
    """

# 3. BOT
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="🎮 Bingo & Wallet Bani", web_app=WebAppInfo(url=RENDER_URL)))
    bot.send_message(message.chat.id, "Baga nagaan dhuftan! Bingo Ethiopia ammayyaa'eera.\n\nTikeetii 1-100 filachuuf, kaffaltii raawwachuuf button gadii fayyadamaa.", reply_markup=markup)

# 4. WEBHOOK
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Forbidden", 403

@app.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Webhook set successfully!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
