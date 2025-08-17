import os
from dotenv import load_dotenv

def load_api_key() -> str:
    """Load the Gemini API key from the .env file."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return api_key
