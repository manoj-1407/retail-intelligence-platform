
from __future__ import annotations
import bcrypt
from fastapi import APIRouter, HTTPException
from ..schemas.auth import TokenRequest, TokenResponse
from ..core.security import create_token
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12))


def _verify(plain: str, stored: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), stored)


# Passwords hashed at startup from env vars. Plaintext never stored.
_USERS: dict[str, dict] = {
    "admin":  {"hash": _hash(settings.admin_password),  "role": "admin"},
    "viewer": {"hash": _hash(settings.viewer_password), "role": "viewer"},
}

# Sentinel hash used for constant-time comparison on unknown usernames.
# Prevents timing-based username enumeration.
_SENTINEL_HASH = _hash("sentinel-value-not-a-real-password")


@router.post("/token", response_model=TokenResponse)
def issue_token(body: TokenRequest) -> TokenResponse:
    entry    = _USERS.get(body.username)
    to_check = entry["hash"] if entry else _SENTINEL_HASH
    match    = _verify(body.password, to_check)

    if not entry or not match:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(access_token=create_token(body.username, entry["role"]))
