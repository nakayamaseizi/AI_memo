import ai_service
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing AI Service...")
print(f"API Key present: {bool(os.getenv('GEMINI_API_KEY'))}")

try:
    result = ai_service.classify_text("明日牛乳を買う")
    print("Result:", result)
except Exception as e:
    print("AI Service Failed:")
    import traceback
    traceback.print_exc()
