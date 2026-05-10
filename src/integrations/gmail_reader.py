import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def fetch_gmail_tasks():
    creds = None
    credentials_path = os.environ.get("GMAIL_CREDENTIALS_JSON_PATH")
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Warning: Gmail token refresh failed - {e}")
                return []
        else:
            if not credentials_path or not os.path.exists(credentials_path):
                print(f"Warning: Gmail credentials JSON not found at {credentials_path}")
                return []
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Warning: Gmail OAuth flow failed - {e}")
                return []
                
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        # 48 hours ago
        past_date = datetime.datetime.now() - datetime.timedelta(hours=48)
        # Using Gmail search syntax
        query = f'is:unread in:inbox after:{int(past_date.timestamp())}'
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        tasks = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            
            snippet = msg_data.get('snippet', '')[:300]
            timestamp_ms = msg_data.get('internalDate', '')
            timestamp = ""
            if timestamp_ms:
                timestamp = datetime.datetime.fromtimestamp(int(timestamp_ms)/1000).isoformat()
                
            tasks.append({
                "source": "gmail",
                "title": subject,
                "description": snippet,
                "sender": sender,
                "timestamp": timestamp,
                "priority": None
            })
            
        print(f"Found {len(tasks)} email tasks from Gmail.")
        return tasks
        
    except HttpError as error:
        print(f"Warning: An error occurred communicating with Gmail API: {error}")
        return []
    except Exception as e:
        print(f"Warning: Unexpected error in Gmail fetch: {e}")
        return []

