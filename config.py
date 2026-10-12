import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
SMALL_MODEL = os.getenv("SMALL_MODEL", "llama-3.1-8b-instant")
LARGE_MODEL = os.getenv("LARGE_MODEL", "llama-3.3-70b-versatile")

PRICES = {
    SMALL_MODEL: {0.0075, 0.30},
    LARGE_MODEL: {0.15, 0.60}
}

CACHE_THRESHOLD = float(os.getenv("CACHE_THRESHOLD", "0.88"))
ROUTE_THRESHOLD = float(os.getenv("ROUTE_THRESHOLD", "0.5"))
CACHE_TTL_SECONDS = 7 * 24 * 3600
TOP_K = 4
DB_PATH = str(BASE_DIR / "tollgate.db")
CHROMA_PATH = str(BASE_DIR / "chroma_data")