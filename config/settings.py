# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN не найден в .env")
if GROQ_API_KEY is None:
    raise ValueError("GROQ_API_KEY не найден в .env")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_MODEL = "openai/gpt-oss-20b"
MAX_HISTORY = 10
LLM_TIMEOUT = 30.0
