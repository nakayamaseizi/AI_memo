import google_docs_service
import json
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

print("Fetching document content...")
try:
    content = google_docs_service.get_doc_content()
    
    print("\n--- Document Structure Analysis ---")
    for index, item in enumerate(content):
        if 'paragraph' in item:
            elements = item['paragraph']['elements']
            paragraph_text = ""
            for element in elements:
                if 'textRun' in element:
                    paragraph_text += element['textRun']['content']
            
            style = item['paragraph'].get('paragraphStyle', {}).get('namedStyleType')
            
            if "メモ" in paragraph_text or "Memo" in paragraph_text:
                print(f"Index {index}:")
                print(f"  Text: {repr(paragraph_text)}")
                print(f"  Style: {style}")
                print(f"  Elements: {json.dumps(elements, ensure_ascii=False)}")
                
except Exception as e:
    print(f"Error: {e}")
