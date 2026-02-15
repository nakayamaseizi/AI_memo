from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
import ai_service
import google_docs_service

# Load environment variables
load_dotenv()

import sys

# Force utf-8 for stdout/stderr to handle emojis in Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Get secrets from .env
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("Error: LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_SECRET is not set in .env")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write("Callback received\n")

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"Body: {body}\n")
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        print(f"Error in callback: {e}")
        import traceback
        traceback.print_exc()
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"Callback Error: {e}\n")
            traceback.print_exc(file=f)
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("--- handle_message called ---") # Debug
    user_message = event.message.text
    print(f"User message: {user_message}") # Debug
    
    # 1. Classify using AI
    print("Calling AI service...") # Debug
    try:
        ai_result = ai_service.classify_text(user_message)
        print(f"AI Result: {ai_result}") # Debug
        category = ai_result.get("category", "Memo")
        summary = ai_result.get("summary", "")
    except Exception as e:
        print(f"AI Service Exception: {e}") # Debug
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"AI Service Exception in app.py: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        
        category = "Memo" # Fallback instead of "Error"
        summary = user_message[:20]
        ai_result = {"reply_message": "申し訳ありません。エラーが発生しましたが、メモとして保存しました。🙇"}

    # 2. Save to Google Doc
    print("Calling Google Docs service...") # Debug
    success = google_docs_service.append_to_doc(category, summary, user_message)

    # 3. Reply to User
    # 3. Reply to User
    if success:
        # Use AI-generated reply if available, otherwise default
        ai_reply = ai_result.get("reply_message")
        if ai_reply:
             reply_text = f"{ai_reply}\n(Category: {category})"
        else:
             reply_text = f"✅ Saved to Google Doc!\nCategory: {category}\nSummary: {summary}"
    else:
        reply_text = "⚠️ Failed to save to Google Doc. Please check server logs."

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=5000)
