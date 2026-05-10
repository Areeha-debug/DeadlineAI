import os

from dotenv import load_dotenv

load_dotenv()

# If running on Streamlit Cloud, we can pass the JSON content directly as an environment variable
# and write it to the file path expected by the rest of the application.
if "GMAIL_CREDENTIALS_JSON" in os.environ:
    with open("./GMAIL_CREDENTIALS.json", "w") as f:
        f.write(os.environ["GMAIL_CREDENTIALS_JSON"])

if "GMAIL_TOKEN_JSON" in os.environ:
    with open("./token.json", "w") as f:
        f.write(os.environ["GMAIL_TOKEN_JSON"])

required_keys = [
    "GROQ_API_KEY",
    "NOTION_API_KEY",
    "NOTION_DATABASE_ID",
    "GMAIL_CREDENTIALS_JSON_PATH"
]

missing_keys = [key for key in required_keys if not os.environ.get(key)]

if missing_keys:
    raise EnvironmentError(
        f"Missing required environment variables: {
            ', '.join(missing_keys)}")
