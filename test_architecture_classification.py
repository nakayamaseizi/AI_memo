import requests
import json
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

def test_classification(text):
    url = "http://127.0.0.1:5000/callback"
    headers = {
        "Content-Type": "application/json",
        "X-Line-Signature": "dummy_signature" 
    }
    
    # Mock LINE event
    data = {
        "destination": "Uxxxxxxxx",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "12345678901234",
                    "text": text
                },
                "timestamp": 1234567890,
                "source": {
                    "type": "user",
                    "userId": "U1234567890abcdef1234567890abcdef"
                },
                "replyToken": "dummy_token"
            }
        ]
    }
    
    print(f"Sending test message: '{text}'")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Status Code: {response.status_code}")
        # Note: real response handled by app.py logic which likely prints to debug.log or returns 200 OK
        # We need to check debug.log for actual classification result
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_classification("エスキス進める")
    test_classification("模型の材料買う")
    test_classification("設計課題の提出")
