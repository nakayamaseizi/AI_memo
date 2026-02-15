import google_docs_service
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Mock data for existing category
category = "TestStylingCat"
item1 = "Item 1"
item2 = "Item 2 (Should be Normal)"
original_text = "ignored"

print(f"1. Creating category '{category}' with item '{item1}'...")
if google_docs_service.append_to_doc(category, item1, original_text):
    print("   -> Success.")
else:
    print("   -> Failed.")
    sys.exit(1)

print(f"2. Appending second item '{item2}' to '{category}'...")
if google_docs_service.append_to_doc(category, item2, original_text):
    print("   -> Success.")
else:
    print("   -> Failed.")
    sys.exit(1)

print("3. Verifying structure and style...")
content = google_docs_service.get_doc_content()

found_cat = False
found_item2 = False
style_correct = False

for item in content:
    if 'paragraph' in item:
        elements = item['paragraph']['elements']
        text = ""
        for elem in elements:
            if 'textRun' in elem:
                text += elem['textRun']['content']
        
        if category in text:
            found_cat = True
            print(f"Found Category: '{text.strip()}'")
            
        if item2 in text:
            found_item2 = True
            print(f"Found Item 2: '{text.strip()}'")
            style = item['paragraph'].get('paragraphStyle', {}).get('namedStyleType')
            print(f"  Style: {style}")
            
            if style == 'NORMAL_TEXT':
                style_correct = True
                print("  -> Style CORRECT (NORMAL_TEXT)")
            else:
                print(f"  -> Style INCORRECT ({style})")

if found_cat and found_item2 and style_correct:
    print("VERIFICATION PASSED")
else:
    print("VERIFICATION FAILED")
