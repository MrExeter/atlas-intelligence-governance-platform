import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

# Only load .env in development
if os.getenv("ENV", "development") == "development":
    load_dotenv(BASE_DIR / ".env")


def get_rate_limit_per_minute() -> int:
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))