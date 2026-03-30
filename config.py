import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("atlas")

BASE_DIR = Path(__file__).resolve().parent
ENV = os.getenv("ENV", "development")

# Only load .env in development
if ENV == "development":
    load_dotenv(BASE_DIR / ".env")

# In production, pull secrets from AWS Secrets Manager and inject into os.environ
# so all existing os.getenv() calls work unchanged.
if ENV == "production":
    from secrets import get_secret

    _SECRETS = {
        "OPENAI_API_KEY":   "atlas/prod/openai-api-key",
        "TOKEN_HASH_SALT":  "atlas/prod/token-hash-salt",
        "TAVILY_API_KEY":   "atlas/prod/tavily-api-key",
        "NEWSDATA_API_KEY": "atlas/prod/newsdata-api-key",
    }

    for env_key, secret_name in _SECRETS.items():
        value = get_secret(secret_name)
        if value:
            os.environ[env_key] = value
        else:
            logger.warning("Secret %s returned empty value", secret_name)


def get_rate_limit_per_minute() -> int:
    return int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
