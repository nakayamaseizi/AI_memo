import requests
import json
import hashlib
import hmac
import base64
import time

# Configuration
CHANNEL_SECRET = "020833126868af25bb076717088107ef" # Replace with your actual channel secret for testing locally if needed, or use the one from .env
# For local testing with the provided app.py, we need the actual secret to generate a valid signature.
# However, since I cannot easily read the .env file in this script without python-dotenv (which might not be installed in the environment where I run this script via python),
# I will assume the user has the secret in .env and the app loads it.
# Actually, I can read .env using standard file io.

def get_channel_secret():
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("LINE_CHANNEL_SECRET"):
                    return line.strip().split("=")[1].strip().strip('"').strip("'")
    except:
        return ""

CHANNEL_SECRET = get_channel_secret()

url = "http://127.0.0.1:5000/callback"

# Message to test
message_text = "牛乳を買う" # "Buy milk" in Japanese

# Create the body
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
            "timestamp": int(time.time() * 1000),
            "source": {
                "type": "user",
                "userId": "U1234567890abcdef1234567890abcdef"
            },
            "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA"
        }
    ]
}

body_str = json.dumps(body, ensure_ascii=False).replace(" ", "") # Line default json dump has no spaces

# Generate signature
hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
    body_str.encode('utf-8'), hashlib.sha256).digest()
signature = base64.b64encode(hash).decode('utf-8')

headers = {
    "Content-Type": "application/json",
    "X-Line-Signature": signature
}

print(f"Sending test message: '{message_text}'")
try:
    response = requests.post(url, headers=headers, data=body_str.encode('utf-8'))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
