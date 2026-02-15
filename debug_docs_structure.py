import google_docs_service
import json
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

try:
    content = google_docs_service.get_doc_content()
    print(json.dumps(content, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
