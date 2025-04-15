from flask import Flask, request, jsonify
import hmac, hashlib, time
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("BINGX_API_KEY")
API_SECRET = os.environ.get("BINGX_API_SECRET")
BASE_URL = "https://open-api.bingx.com"
SYMBOL = "ADA-USDT"

def sign(params):
    sorted_params = sorted(params.items())
    query = '&'.join(f"{k}={v}" for k, v in sorted_params)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return signature


def place_order(side):
    endpoint = '/openApi/swap/v2/trade/order'
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

    params['signature'] = sign(params)
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-BX-APIKEY': API_KEY
}


    response = requests.post(url, data=params, headers=headers)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'action' in data:
        result = place_order(data['action'])
        return jsonify(result)
    return jsonify({'error': 'no action'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
