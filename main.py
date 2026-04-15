from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# User database (Fakkeenyaaf)
users_db = {
    "user_1": {"balance": 1000.0, "name": "Abbebe"}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    method = data.get('method') # Telebirr, CBE_Birr, CBE
    amount = data.get('amount')
    action = data.get('action') # deposit ykn withdraw

    if action == "deposit":
        # Linkii kaffaltii kallaattiin uumuu (Fakkeenyaaf)
        return jsonify({
            "status": "success",
            "msg": f"Gara {method}-itti isin geessaa jira...",
            "url": f"https://payment-gateway.et/{method.lower()}/pay?amt={amount}"
        })
    
    elif action == "withdraw":
        # Baasii galmeessuu
        return jsonify({
            "status": "success",
            "msg": f"Gaffiin baasii herrega {method} keessaniin fudhatameera. Sa'aatii 24 keessatti siif kaffalama."
        })

if __name__ == '__main__':
    app.run(debug=True)
