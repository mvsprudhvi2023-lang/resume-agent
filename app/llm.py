import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=API_KEY)

# Main model first, then backups (duplicates removed)
MODELS = list(dict.fromkeys([MODEL, FALLBACK_MODEL, "gemini-2.5-flash-lite"]))
RETRY_CODES = {429, 500, 503}
ATTEMPTS = 4


def ask_llm(prompt: str) -> str:
    last_error = None
    for model in MODELS:
        for attempt in range(ATTEMPTS):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text
            except errors.APIError as e:
                last_error = e
                if e.code in RETRY_CODES:
                    if attempt < ATTEMPTS - 1:
                        time.sleep(3 * (attempt + 1))  # waits 3s, 6s, 9s
                elif e.code == 404:
                    break  # model name not found, try the next model
                else:
                    raise
    raise last_error