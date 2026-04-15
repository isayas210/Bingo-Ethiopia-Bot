import os
from flask import Flask, render_template
from telebot import TeleBot

# Token bot keetii as keessa galchi
TOKEN = "8692359063:AAHteqfebC808tTmj6qvIdjiVJIXoRTf4c"
bot = TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
