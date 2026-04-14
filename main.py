import os
import telebot
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# 1. SETUP
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

RENDER_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"

# 2. MINI APP LOGIC (Bingo Engine)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="or">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia 1-1000</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: sans-serif; background: #001f3f; color: white; text-align: center; padding: 15px; margin: 0; }
            .card { background: #003366; padding: 20px; border-radius: 15px; border: 1px solid #00d4ff; }
            h1 { color: #ffcc00; font-size: 22px; }
            .wallet { font-size: 14px; color: #00ffcc; margin-bottom: 15px; }
            input { padding: 10px; width: 80%; border-radius: 5px; border: none; margin: 10px 0; font-size: 16px; }
            .btn { background: #28a745; color: white; padding: 12px; border: none; border-radius: 8px; width: 90%; font-weight: bold; cursor: pointer; }
            #bingo-area { display: none; margin-top: 20px; }
            .called-number { font-size: 40px; color: #ffcc00; font-weight: bold; background: #002b55; padding: 10px; border-radius: 50%; width: 80px; height: 80px; line-height: 80px; margin: 20px auto; border: 3px solid #ffcc00; }
            .history { font-size: 12px; background: #001a33; padding: 10px; border-radius: 5px; height: 60px; overflow-y: auto; }
            .payout-msg { color: #2ecc71; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Bingo Ethiopia</h1>
            <div class="wallet">Balance: 0.00 ETB</div>

            <div id="selection-area">
                <p>Lakkofsa Tikeetii Filadhu (1-1000):</p>
                <input type="number" id="ticketInput" min="1" max="1000" placeholder="Fkn: 452">
                <button class="btn" onclick="startBingo()">🎟️ Tikeetii Kutadhu</button>
            </div>

            <div id="bingo-area">
                <p>Tikeetii Kee: <span id="myTicket" style="color: #ffcc00; font-weight: bold;"></span></p>
                <div class="called-number" id="currentNum">?</div>
                <p>Lakkofsota dhufran:</p>
                <div class="history" id="history">---</div>
                <div id="winMsg" class="payout-msg"></div>
            </div>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();

            let calledNumbers = [];
            let myTicket = 0;

            function startBingo() {
                let input = document.getElementById('ticketInput').value;
                if (input < 1 || input > 1000) {
                    alert("Maaloo 1 hanga 1000 gidduu filadhu!");
                    return;
                }
                myTicket = parseInt(input);
                document.getElementById('selection-area').style.display = 'none';
                document.getElementById('bingo-area').style.display = 'block';
                document.getElementById('myTicket').innerText = myTicket;
                
                // Lakkofsa waamuu jalqabi
                nextNumber();
            }

            function nextNumber() {
                if (calledNumbers.length >= 1000) return;

                let num;
                do {
                    num = Math.floor(Math.random() * 1000) + 1;
                } while (calledNumbers.includes(num));

                calledNumbers.push(num);
                document.getElementById('currentNum').innerText = num;
                document.getElementById('history').innerText = calledNumbers.join(', ');

                // Mo'achuu mirkaneessi (Line 1 check - tapha kana keessatti tikeetiin kee yoo dhufe)
                if (num === myTicket) {
                    let bet = 10; // Fknf qarshii 10 qabsiisne
                    let winAmount = bet * 0.70;
                    document.getElementById('winMsg').innerHTML = `🎊 BINGO! Mo'atteetta!<br>Qarshii Win: ${winAmount} ETB (70%)`;
                    tg.MainButton.setText("Maallaqa Fudhu").show();
                } else {
                    setTimeout(nextNumber, 3000); // Sekondii 3 booda lakk. itti aanu
                }
            }
        </script>
    </body>
    </html>
    """

# 3. BOT (Nagaa qofa)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = WebAppInfo(url=RENDER_URL)
    button = KeyboardButton(text="🎮 Bingo 1-1000 Jalqabi", web_app=web_app)
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        "Baga nagaan dhuftan! Bingo Ethiopia lakkofsa 1-1000 qabu qophaa'eera.\n\nTikeetii filachuuf button gadii fayyadamaa.", 
        reply_markup=markup
    )

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
