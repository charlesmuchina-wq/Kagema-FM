"""
Anonymous device identity.

Issues a stable, server-backed user id plus a signed token on first launch,
replacing the previous purely client-generated local id. There is no login UI:
each install registers once and stores the token. The token can gate
authenticated endpoints later; existing endpoints that accept a ``user_id`` keep
working with the issued id, so this is additive.
"""
import os
import uuid
from datetime import datetime, timezone

import jwt

from db import get_db

JWT_ALGORITHM = "HS256"


def _secret():
    """JWT signing secret. Set a strong JWT_SECRET in production; the dev fallback
    is intentionally obvious and must not be used for real deployments."""
    return os.getenv("JWT_SECRET", "dev-insecure-change-me")


def issue_token(user_id):
    """Return a signed token carrying the user id."""
    payload = {
        "sub": user_id,
        "type": "anonymous",
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def verify_token(token):
    """Return the user id from a valid token, or None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None


def bearer_token(authorization):
    """Extract the token from an 'Authorization: Bearer <token>' header value."""
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


async def create_anonymous_user():
    """Create a new anonymous user record and return (user_id, token)."""
    user_id = f"user_{uuid.uuid4().hex}"
    await get_db().users.insert_one(
        {
            "id": user_id,
            "type": "anonymous",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return user_id, issue_token(user_id)
