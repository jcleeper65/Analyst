import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY", "")
print(api_key[:4] + "...")
print(os.getenv("SEC_USER_AGENT", ""))
