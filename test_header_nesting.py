import google_docs_service
import sys
import json

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Mock data
category = "TestNewHeader"
summary = "TestItem"
original_text = "ignored"

print(f"Appending new category '{category}' with item '{summary}'...")

if google_docs_service.append_to_doc(category, summary, original_text):
    print("Append successful.")
    
    # Check structure
    print("Checking document structure...")
    content = google_docs_service.get_doc_content()
    
    # We expect the last few paragraphs to be:
    # ...
    # Paragraph: \n (Normal)
    # Paragraph: TestNewHeader\n (Heading 2, No Bullet)
    # Paragraph: TestItem\n (Checkbox)
    
    found_header = False
    found_item = False
    header_correct = False
    
    for item in content:
        if 'paragraph' in item:
            elements = item['paragraph']['elements']
            text = ""
            for elem in elements:
                if 'textRun' in elem:
                    text += elem['textRun']['content']
            
            if category in text:
                found_header = True
                print(f"Found header: '{text.strip()}'")
                
                # Check style
                style = item['paragraph'].get('paragraphStyle', {}).get('namedStyleType')
                bullet = item['paragraph'].get('bullet')
                
                print(f"  Style: {style}")
                print(f"  Bullet: {bullet}")
                
                if style == 'HEADING_2' and bullet is None:
                    header_correct = True
                    print("  -> Header style correct (HEADING_2, No Bullet)")
                else:
                    print("  -> Header style INCORRECT")
                    
            if summary in text:
                 found_item = True
                 print(f"Found item: '{text.strip()}'")
                 bullet = item['paragraph'].get('bullet')
                 if bullet:
                     print("  -> Item has bullet (Correct)")
                 else:
                     print("  -> Item missing bullet")

    if header_correct and found_item:
        print("VERIFICATION PASSED")
    else:
        print("VERIFICATION FAILED")

else:
    print("Append failed.")
