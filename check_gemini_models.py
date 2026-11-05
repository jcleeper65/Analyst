import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
client = genai.Client(api_key=key)

for model in ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]:
    try:
        response = client.models.generate_content(model=model, contents="Reply with OK.")
        print(f"{model}: WORKS - {response.text}")
    except Exception as e:
        print(f"{model}: FAILED - {str(e)[:200]}")
