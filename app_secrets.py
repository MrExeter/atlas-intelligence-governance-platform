import json
import logging
import os

logger = logging.getLogger("atlas")


def get_secret(secret_name: str) -> str:
    """
    Fetch a secret value.
    - Production: AWS Secrets Manager
    - Development: os.environ (already loaded from .env by config.py)
    """
    if os.getenv("ENV", "development") != "production":
        # In dev the env var name is the last segment of the secret path
        env_key = secret_name.split("/")[-1].upper().replace("-", "_")
        return os.getenv(env_key, "")

    import boto3
    from botocore.exceptions import ClientError

    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-west-1"))
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error("Failed to fetch secret %s: %s", secret_name, e)
        raise

    secret = response.get("SecretString", "")

    # Secrets Manager can store JSON or plain strings
    try:
        parsed = json.loads(secret)
        # If it's a single-key JSON object, return the value
        if isinstance(parsed, dict) and len(parsed) == 1:
            return next(iter(parsed.values()))
        return secret
    except (json.JSONDecodeError, TypeError):
        return secret
