import telebot
from flask import Flask, render_template_string
import os
from threading import Thread

# Token kee isa sirrii
BOT_TOKEN = "8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoXRTf4c"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Fuula Bingo keetii (User Interface)
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bingo Ethiopia</title>
        <style>
            body { 
                background-color: #1a1a1a; 
                color: white; 
                text-align: center; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                padding-top: 50px; 
            }
            .container {
                border: 2px solid #0088cc;
                display: inline-block;
                padding: 20px;
                border-radius: 15px;
                background-color: #2c2c2c;
            }
            h1 { color: #0088cc; }
            .btn {
                background-color: #0088cc;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bingo Ethiopia</h1>
            <p>Baga Gammaddan! Appiin keessan hojjechaa jira.</p>
            <br>
            <p>Tapha jalqabuuf Bot keessan irratti "Play" tuqaa.</p>
        </div>
    </body>
    </html>
    """

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask kallaattiin dursa akka dammaquuf
    t = Thread(target=run)
    t.start()
    
    # Telegram Bot Webhook akka hin uumamneef delete goona
    bot.remove_webhook()
    print("Bot is polling...")
    bot.polling(none_stop=True)
