import requests
import json
import time
from requests_oauthlib import OAuth1
from datetime import datetime, timedelta

class EtradeAuth:
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_oauth(self):
        return OAuth1(
            self.config['api_key'],
            client_secret=self.config['api_secret'],
            resource_owner_key=self.config['params']['oauth_token'],
            resource_owner_secret=self.config['params']['oauth_token_secret']
        )

    def get_access_token(self):
        response = requests.post(
            self.config['access_token_url'],
            auth=self.get_oauth()
        )

        if response.status_code == 200:
            response_text = response.text
            params = dict(item.split("=") for item in response_text.split("&"))

            self.config['params']['oauth_token'] = params['oauth_token']
            self.config['params']['oauth_token_secret'] = params['oauth_token_secret']
            self.save_config()
            return True
        else:
            return False

    def get_request_token(self):
        response = requests.post(
            self.config['token_url'],
            auth=self.get_oauth()
        )

        if response.status_code == 200:
            response_text = response.text
            params = dict(item.split("=") for item in response_text.split("&"))

            self.config['params']['oauth_token'] = params['oauth_token']
            self.config['params']['oauth_token_secret'] = params['oauth_token_secret']
            self.config['headers']['oauth_callback'] = self.config['callback_url']
            self.save_config()

            return f"{self.config['authorize_url']}?oauth_token={params['oauth_token']}"
        else:
            return False

    def refresh_token(self):
        oauth = self.get_oauth()

        response = requests.post(
            self.config['access_token_url'],
            auth=oauth,
            headers=self.config['headers'],
            data=self.config['params']
        )

        if response.status_code == 200:
            response_text = response.text
            params = dict(item.split("=") for item in response_text.split("&"))

            self.config['params']['oauth_token'] = params['oauth_token']
            self.config['params']['oauth_token_secret'] = params['oauth_token_secret']
            self.save_config()
            return True
        else:
            return False
    
    def get_auth_url(self):
        request_token_url = self.get_request_token()
        if request_token_url:
            return request_token_url
        else:
            return False