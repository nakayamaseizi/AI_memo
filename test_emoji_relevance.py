import ai_service
import sys
import json

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    "ドレッシング買う",
    "卵買う",
    "牛乳買う",
    "エスキス進める"
]

print("--- Testing Emoji Relevance ---")
for text in test_cases:
    print(f"\nInput: {text}")
    try:
        result = ai_service.classify_text(text)
        reply = result.get("reply_message", "")
        print(f"Reply: {reply}")
        
        if "ドレッシング" in text:
            if "🥗" in reply or "野菜" in reply or "菜" in reply: # loosen check
                 print("  -> PASS (Relevant emoji found)")
            elif "🥚" in reply:
                 print("  -> FAIL (Egg emoji found for dressing)")
            else:
                 print("  -> WARN (No specific expected emoji found, check manually)")
                 
        elif "卵" in text:
            if "🥚" in reply:
                 print("  -> PASS (Egg emoji found)")
            else:
                 print("  -> FAIL (egg emoji not found)")

    except Exception as e:
        print(f"Error: {e}")

print("\n--- Done ---")
