import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a model that is available in the list
model = genai.GenerativeModel('gemini-2.0-flash')

def classify_text(text):
    """
    Classifies the input text into a category and provides a summary.
    Returns a JSON object with 'category' and 'summary'.
    """
    prompt = f"""
    You are a helpful assistant that classifies and summarizes text messages for a 4th-year architecture student at Kagoshima University.
    
    Please analyze the following text:
    "{text}"
    
    1. Classify it into ONE of these categories:
       - [建築課題] : Architecture assignments, esquisse, models, design work. PRIORITIZE this if keywords like "エスキス", "模型", "設計", "課題" are present, even if it involves buying something (e.g., "Buy model materials").
       - [やることリスト] : Tasks or things to do
       - [予定] : Events with dates or times
       - [買い物リスト] : Items to buy (Groceries, daily necessities, etc.)
       - [メモ] : General information or logs
       
    2. Provide a VERY SHORT, NOUN-BASED summary (max 5 words).
       IMPORTANT:
       - The summary MUST be in Japanese.
       - Use ONLY nouns if possible (e.g., "牛乳" instead of "牛乳を買う").
       - Remove verbs like "buy", "eat", "go to" etc.
       - Example: "Buy milk" -> "牛乳", "Go to park" -> "公園"
    
    3. Generate a "reply_message" for the user.
       - The tone should be POLITE, ENCOURAGING, and SUPPORTIVE.
       - Do NOT use "robot" or "robo" language.
       - Act like a capable human assistant or secretary.
       - Use RELEVANT emojis based on the content.
         - Buying vegetables -> 🥦, 🥕
         - Buying meat -> 🥩
         - Buying dressing -> 🥗
         - Buying eggs -> 🥚
         - Architecture/Study -> 📚, ✏️, 🏗️, 🏛️
       - Avoid defaulting to the same emoji (like 🥚) for everything.
       - If it's an assignment (建築課題), say something like "課題の進行、応援しています！✨".
       - Keep it short (1-2 sentences).
       - Examples:
         - "了解しました！課題、応援しています✨"
         - "メモしました。忘れずに！"
         - "お買い物ですね。行ってらっしゃいませ🥗" (if buying salad/dressing)

    4. Return the result strictly in JSON format like this:
    {{
        "category": "CategoryName",
        "summary": "Noun-based summary",
        "reply_message": "Your polite reply here"
    }}
    """
    
    
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"Processing text: {text}\n")
    
    import time
    
    max_retries = 3
    base_delay = 2 # seconds
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_text)
            
            # Normalize Category
            valid_categories = {
                "shopping": "買い物リスト",
                "shopping list": "買い物リスト",
                "[shopping]": "買い物リスト",
                "[買い物リスト]": "買い物リスト",
                "todo": "やることリスト",
                "[todo]": "やることリスト",
                "[やることリスト]": "やることリスト",
                "schedule": "予定",
                "[schedule]": "予定",
                "[予定]": "予定",
                "idea": "アイデア",
                "[idea]": "アイデア",
                "[アイデア]": "アイデア",
                "architecture": "建築課題",
                "[architecture]": "建築課題",
                "assignment": "建築課題",
                "[assignment]": "建築課題",
                "esquisse": "建築課題",
                "[esquisse]": "建築課題",
                "model": "建築課題",
                "[model]": "建築課題",
                "建築課題": "建築課題",
                "[建築課題]": "建築課題",
                "memo": "メモ",
                "[memo]": "メモ",
                "[メモ]": "メモ"
            }
            
            raw_category = result.get("category", "").lower().strip()
            # Remove brackets if strictly surrounding
            if raw_category.startswith("[") and raw_category.endswith("]"):
                 raw_category_content = raw_category[1:-1]
                 if raw_category_content in valid_categories: # recursive check if needed, but let's just allow map to handle keys
                     pass

            if raw_category in valid_categories:
                result["category"] = valid_categories[raw_category]
            
            # Final fallback if it's still English or unknown, maybe keep it?
            # Or enforce one of the Japanese keys?
            # For now, if it matches our map, we update it.
            
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"Success: {json.dumps(result, ensure_ascii=False)}\n")
                
            return result
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) # Exponential backoff: 2, 4, 8
                with open("debug.log", "a", encoding="utf-8") as f:
                    f.write(f"Rate limit hit (429). Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})\n")
                time.sleep(delay)
                continue
            
            # If last attempt or other error
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write(f"Error: {e}\n")
                import traceback
                traceback.print_exc(file=f)
            
            if attempt == max_retries - 1 or "429" not in str(e):
                 # Fallback
                return {
                    "category": "メモ", 
                    "summary": text[:20],
                    "reply_message": "申し訳ありません。AIの接続が不安定ですが、メモとして保存しました。🙇"
                }
