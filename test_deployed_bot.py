import sys
import os
import json
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from linebot.utils import SignatureValidator
import hashlib
import hmac
import base64
from dotenv import load_dotenv

# Load local environment variables for credentials
load_dotenv()

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if not CHANNEL_SECRET:
    print("Error: LINE_CHANNEL_SECRET is not set in .env")
    sys.exit(1)

def send_test_request(target_url, message_text="デプロイ確認"):
    print(f"--- Testing Deployed Bot at {target_url} ---")
    
    # Create valid signature
    body = json.dumps({
        "destination": "U00000000000000000000000000000000",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "00000000000000",
                    "text": message_text
                },
                "timestamp": 1625667243123,
                "source": {
                    "type": "user",
                    "userId": "U00000000000000000000000000000000"
                },
                "replyToken": "00000000000000000000000000000000",
                "mode": "active"
            }
        ]
    })
    
    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'),
                    body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'X-Line-Signature': signature
    }
    
    try:
        response = requests.post(target_url, headers=headers, data=body)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Request sent successfully!")
            print("Check your Google Doc to see if the message was saved.")
        else:
            print("\n❌ Request failed. Check the server logs on Render.")
            
    except Exception as e:
        print(f"\n❌ Error sending request: {e}")

if __name__ == "__main__":
    print("Paste your Render URL (must end with /callback)")
    print("Example: https://your-app-name.onrender.com/callback")
    target_url = input("Enter URL: ").strip()
    
    if not target_url:
        print("URL is required.")
    elif not target_url.endswith("/callback"):
        print("Warning: URL should usually end with /callback. Appending it...")
        target_url += "/callback"
        
    send_test_request(target_url)
