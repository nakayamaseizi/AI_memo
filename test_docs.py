import google_docs_service
from dotenv import load_dotenv

load_dotenv()

print("Testing Google Docs Service...")

try:
    result = google_docs_service.append_to_doc("TestCategory", "Test Summary", "Test Original Text")
    print(f"Result: {result}")
except Exception as e:
    print("Google Docs Service Failed:")
    import traceback
    traceback.print_exc()
