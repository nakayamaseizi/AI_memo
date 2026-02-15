import requests
import json
import hashlib
import hmac
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

def create_signature(secret, body):
    hash = hmac.new(secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode('utf-8')
    return signature

def send_test_request(message_text):
    url = 'http://localhost:5000/callback'
    
    body = {
        "destination": "Uxxxxxxxx",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "12345678901234",
                    "text": message_text
                },
                "timestamp": 1625667243123,
                "source": {
                    "type": "user",
                    "userId": "U1234567890abcdef1234567890abcdef"
                },
                "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA"
            }
        ]
    }
    
    body_str = json.dumps(body)
    signature = create_signature(CHANNEL_SECRET, body_str)
    
    headers = {
        'Content-Type': 'application/json',
        'X-Line-Signature': signature,
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    
    try:
        response = requests.post(url, headers=headers, data=body_str)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    print("Sending test message: '牛乳を買う'")
    send_test_request("牛乳を買う")
