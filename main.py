import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Fake database for balance
user_wallet = {"balance": 500.00}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/payment', methods=['POST'])
def handle_payment():
    data = request.json
    method = data.get('method')
    amount = data.get('amount')
    action = data.get('action') # deposit ykn withdraw

    if action == "deposit":
        # Linkii kaffaltii kallaattiin uumuu
        pay_url = f"https://payment-gateway.et/pay?method={method}&amt={amount}"
        return jsonify({
            "status": "success", 
            "url": pay_url, 
            "msg": f"Gara kaffaltii {method}-itti isin geessaa jira..."
        })
    
    else:
        # Withdraw: Barreeffamni 'Admin qunnamaa' jedhu asitti dhabameera
        return jsonify({
            "status": "success", 
            "msg": f"Gaffiin baasii {amount} ETB karaa {method} fudhatameera. Sa'aatii 24 keessatti herrega keessan irratti ni dhangala'a."
        })

if __name__ == '__main__':
    # RENDER IRRATTI DOGOGGORA PORT SANA KAN SIRREESSU KANA:
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
