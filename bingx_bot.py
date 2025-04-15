from flask import Flask, request, jsonify
import hmac, hashlib, time, os
import requests

app = Flask(__name__)

API_KEY = os.environ.get("BINGX_API_KEY")
API_SECRET = os.environ.get("BINGX_API_SECRET")
BASE_URL = "https://open-api.bingx.com"
SYMBOL = "ADA-USDT"

def sign(params):
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

def place_order(side):
    endpoint = "/openApi/swap/v2/trade/order"
    url = BASE_URL + endpoint

    timestamp = str(int(time.time() * 1000))
    params = {
        "apiKey": API_KEY,
        "symbol": SYMBOL,
        "side": side.upper(),
        "positionSide": "LONG" if side == "buy" else "SHORT",
        "type": "MARKET",
        "quantity": 50,
        "timestamp": timestamp
    }

    params['signature'] = sign(params)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-BX-APIKEY": API_KEY
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

# Pornire aplicație (pentru Render)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
