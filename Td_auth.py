import requests
import json
import time
from datetime import datetime, timedelta

class TDAuth:
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        if isinstance(self.config_file, str):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        elif isinstance(self.config_file, dict):
            self.config = self.config_file
        else:
            raise ValueError("config_file must be a file path or a dictionary object")

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_auth_headers(self):
        return {
            "Authorization": f"Bearer {self.config['access_token']}"
        }

    def get_access_token(self):
        response = requests.post(
            self.config['token_url'],
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.config['refresh_token'],
                "access_type": "offline",
                "client_id": self.config['client_id'],
                "redirect_uri": self.config['redirect_uri'],
                "client_secret": self.config['client_secret']
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            self.config['access_token'] = response_data['access_token']
            self.config['refresh_token'] = response_data['refresh_token']
            self.config['expires_at'] = datetime.utcnow() + timedelta(seconds=response_data['expires_in'])
            self.save_config()
            return True
        else:
            return False

    def authorize(self, code):
        response = requests.post(
            self.config['access_token_url'],
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "access_type": "offline",
                "client_id": self.config['client_id'],
                "redirect_uri": self.config['redirect_uri'],
                "client_secret": self.config['client_secret']
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            self.config['access_token'] = response_data['access_token']
            self.config['refresh_token'] = response_data['refresh_token']
            self.config['expires_at'] = datetime.utcnow() + timedelta(seconds=response_data['expires_in'])
            self.save_config()
            return True
        else:
            return False

    def refresh_token_if_needed(self):
        if 'expires_at' not in self.config or datetime.utcnow() >= self.config['expires_at']:
            self.get_access_token()

    def get_authorization_url(self):
        params = {
            "response_type": "code",
            "redirect_uri": self.config['redirect_uri'],
            "client_id": self.config['client_id']
        }

        url = f"{self.config['authorize_url']}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return url