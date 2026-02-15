import ai_service
import sys
import json

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    "エスキス進める",
    "模型の材料買う",
    "設計課題の提出",
    "のり買う", # Should be Shopping
    "12時に集合" # Should be Schedule
]

print("--- Testing Architecture Classification ---")
for text in test_cases:
    print(f"\nInput: {text}")
    result = ai_service.classify_text(text)
    print(f"Output: {json.dumps(result, ensure_ascii=False)}")
    
    category = result.get("category")
    if "エスキス" in text or "模型" in text or "設計" in text:
        if category == "建築課題":
             print("  -> PASS (Correctly classified as 建築課題)")
        else:
             print(f"  -> FAIL (Expected 建築課題, got {category})")
    elif "のり" in text:
         if category == "買い物リスト":
              print("  -> PASS (Correctly classified as 買い物リスト)")
         else:
              print(f"  -> FAIL (Expected 買い物リスト, got {category})")

print("\n--- Done ---")
