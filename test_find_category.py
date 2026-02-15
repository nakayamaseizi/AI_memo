import google_docs_service
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

print("Fetching document content...")
content = google_docs_service.get_doc_content()

categories_to_test = ["メモ", "Memo", "買い物リスト"]

for cat in categories_to_test:
    print(f"Searching for '{cat}'...")
    index = google_docs_service.find_category_index(content, cat)
    if index:
        print(f"  FAILED? Found at index {index} (Expected behavior involves checking if this is correct)")
        print(f"  Found '{cat}' at index {index}")
    else:
        print(f"  NOT FOUND '{cat}'")

print("Done.")
