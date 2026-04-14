import threading

# Koodii Flask kee booda, bot-icha akkanatti jalqabsiisi:
def run_bot():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    # Bot-icha thread addaatiin banuuf
    threading.Thread(target=run_bot).start()
    # Flask immoo asitti kallaattiin bana
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
