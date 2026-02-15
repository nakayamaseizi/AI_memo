import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/documents']
SERVICE_ACCOUNT_FILE = 'service_account.json'
DOCUMENT_ID = os.getenv('GOOGLE_DOC_ID')

import json

def get_service():
    # Check for credentials in environment variable (Render/Cloud)
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES)
    else:
        # Fallback to local file
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
    service = build('docs', 'v1', credentials=creds)
    return service

def get_doc_content():
    service = get_service()
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    return doc.get('body', {}).get('content', [])

def find_category_index(content, category):
    """
    Finds the end index of the paragraph containing the category header.
    Returns None if not found.
    """
    for item in content:
        if 'paragraph' in item:
            elements = item['paragraph']['elements']
            for element in elements:
                if 'textRun' in element:
                    text = element['textRun']['content'].strip()
                    if text.lower() == category.lower():
                        return item['paragraph']['elements'][-1]['endIndex'] - 1
    return None

def append_to_doc(category, summary, original_text):
    """
    Appends the message to the Google Doc under the matching category header.
    Uses interactive checkboxes for the summary.
    """
    try:
        service = get_service()
        content = get_doc_content()
        
        if not content:
            print("Error: Document content is empty.")
            return False
            
        insert_index = find_category_index(content, category)
        requests = []

        # Text structure:
        # \n
        # {summary}  <- This will be a checkbox
        # {original_text} <- Indented text
        
        summary_text = f"{summary}"
        # details_text = f"\n   {original_text}" # Indent details

        if insert_index:
            # Insert after the found header
            start_index = insert_index
            
            # 1. Insert Newline + Summary
            requests.append({
                'insertText': {
                    'location': {'index': start_index},
                    'text': '\n' + summary_text
                }
            })
            
            # 2. Apply Checkbox to "Summary"
            # Range is from (start_index + 1) to (start_index + 1 + len(summary_text))
            # Note: Adding '\n' increases index by 1.
            summary_start = start_index + 1
            summary_end = summary_start + len(summary_text)

            # Enforce NORMAL_TEXT style (Fix for inheritance issue)
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': summary_start,
                        'endIndex': summary_end
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                    },
                    'fields': 'namedStyleType'
                }
            })

            requests.append({
                'createParagraphBullets': {
                    'range': {
                        'startIndex': summary_start,
                        'endIndex': summary_end
                    },
                    'bulletPreset': 'BULLET_CHECKBOX'
                }
            })

        else:
            # Append to end
            end_index = content[-1]['endIndex'] - 1
            
            # Logic:
            # 1. Insert \n (to end previous paragraph)
            # 2. Insert header text
            # 3. Apply HEADING_2 to header
            # 4. Remove bullets from header (critical!)
            # 5. Insert \n + summary
            # 6. Apply checkbox to summary

            requests.append({
                'insertText': {
                    'location': {'index': end_index},
                    'text': '\n'  # Ensure we are on a new line
                }
            })
            
            # Update end_index after insertion
            header_start = end_index + 1
            
            header_content = f"{category}\n"
            requests.append({
                'insertText': {
                    'location': {'index': header_start},
                    'text': header_content
                }
            })
            
            header_end = header_start + len(header_content)

            # Apply Heading Style & Remove Bullets for Header
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': header_start,
                        'endIndex': header_end - 1 # Exclude newline to avoid affecting next paragraph
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2',
                    },
                    'fields': 'namedStyleType'
                }
            })
            
            # Explicitly remove bullets from the header paragraph
            requests.append({
                'deleteParagraphBullets': {
                    'range': {
                        'startIndex': header_start,
                        'endIndex': header_end - 1
                    }
                }
            })

            # Now insert the summary as a checkbox
            summary_start = header_end
            summary_content = f"{summary}"
            
            requests.append({
                'insertText': {
                    'location': {'index': summary_start},
                    'text': summary_content
                }
            })
            
            summary_end = summary_start + len(summary_content)

            # Enforce NORMAL_TEXT style (Safeguard)
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': summary_start,
                        'endIndex': summary_end
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                    },
                    'fields': 'namedStyleType'
                }
            })

            requests.append({
                'createParagraphBullets': {
                    'range': {
                        'startIndex': summary_start,
                        'endIndex': summary_end
                    },
                    'bulletPreset': 'BULLET_CHECKBOX'
                }
            })

        service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()
        return True
    except Exception as e:
        print(f"Error appending to Google Doc: {e}")
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"Error in Google Docs append: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        return False
