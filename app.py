from flask import Flask, render_template, request, jsonify
from Etrade_auth import EtradeAuth
from Td_auth import TDAuth
import json

app = Flask(__name__)

# Load config file
with open('config.json') as f:
    config = json.load(f)

# Initialize authentication classes
etrade_auth = EtradeAuth('config.json')
td_auth = TDAuth({'client_id': config['td_ameritrade']['client_id'], 'redirect_uri': config['td_ameritrade']['redirect_uri']})

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/etrade-auth')
def etrade_authenticate():
    auth_url = etrade_auth.get_auth_url()
    return render_template('etrade-auth.html', auth_url=auth_url)

@app.route('/etrade-token')
def etrade_token():
    oauth_verifier = request.args.get('oauth_verifier')
    access_token = etrade_auth.get_access_token(oauth_verifier)
    return jsonify(access_token)

@app.route('/tdameritrade-auth')
def tdameritrade_authenticate():
    auth_url = td_auth.get_auth_url()
    return render_template('tdameritrade-auth.html', auth_url=auth_url)

@app.route('/tdameritrade-token')
def tdameritrade_token():
    code = request.args.get('code')
    access_token = td_auth.get_access_token(code)
    return jsonify(access_token)

if __name__ == '__main__':
    app.run(debug=True)