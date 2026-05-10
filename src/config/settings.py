import os
from dotenv import load_dotenv

load_dotenv()

required_keys = [
    "OPENAI_API_KEY",
    "NOTION_API_KEY",
    "NOTION_DATABASE_ID",
    "GMAIL_CREDENTIALS_JSON_PATH"
]

missing_keys = [key for key in required_keys if not os.environ.get(key)]

if missing_keys:
    raise EnvironmentError(
        f"Missing required environment variables: {
            ', '.join(missing_keys)}")
