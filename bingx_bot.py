from flask import Flask, request, jsonify
import hmac, hashlib, time
import os
import requests

app = Flask(__name__)

API_KEY = os.environ.get("BINGX_API_KEY")
API_SECRET = os.environ.get("BINGX_API_SECRET")
BASE_URL = "https://open-api.bingx.com"
SYMBOL = "ADA-USDT"

# Semnare HMAC SHA256

def sign(params, secret):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# Funcție de plasare ordine

def place_order(side):
    endpoint = "/openApi/swap/v2/trade/order"
    url = BASE_URL + endpoint

    timestamp = str(int(time.time() * 1000))
    params = {
        'apiKey': API_KEY,
        'symbol': SYMBOL,
        'side': side.upper(),
        'positionSide': 'LONG' if side == 'buy' else 'SHORT',
        'type': 'MARKET',
        'quantity': 50,
        'timestamp': timestamp
    }

    params['signature'] = sign(params, API_SECRET)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-BX-APIKEY': API_KEY
    }

    response = requests.post(url, headers=headers, data=params)
    return response.json()

# Ruta webhook

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")
    if action == "buy":
        result = place_order("buy")
    elif action == "sell":
        result = place_order("sell")
    else:
        result = {"error": "Unknown action"}
    return jsonify(result)

# Pornire aplicație (opțional pentru local dev)
if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
