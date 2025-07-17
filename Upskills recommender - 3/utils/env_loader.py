from dotenv import load_dotenv
import os

def load_env_variables():
    load_dotenv()
    youtube_key = os.getenv("YOUTUBE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not youtube_key:
        print("[Warning] YOUTUBE_API_KEY not set in .env file")
    if not gemini_key:
        print("[Warning] GEMINI_API_KEY not set in .env file")

    return {
        "YOUTUBE_API_KEY": youtube_key,
        "GEMINI_API_KEY": gemini_key
    }