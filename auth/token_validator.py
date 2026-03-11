import os
import hashlib
from typing import Optional
from datetime import datetime, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, status

import boto3
from fastapi import HTTPException, Request

security = HTTPBearer()

TOKEN_HASH_SALT = os.getenv("TOKEN_HASH_SALT")
AWS_REGION = os.getenv("AWS_REGION", "us-west-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "atlas_invite_tokens")

if not TOKEN_HASH_SALT:
    raise RuntimeError("TOKEN_HASH_SALT not configured")


dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def hash_token(token: str) -> str:
    combined = f"{token}{TOKEN_HASH_SALT}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


async def validate_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
):

    if request.method == "OPTIONS":
        return

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token_hash = hash_token(token)

    response = table.get_item(Key={"token_hash": token_hash})
    item = response.get("Item")

    if not item or not item.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    expires_raw = item.get("expires_at")
    if not expires_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    expires_at = datetime.fromisoformat(expires_raw)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
