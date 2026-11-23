import os
import hmac
import hashlib
import secrets
import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_CONFIGURED_SECRET = os.getenv("SECRET_KEY")
if _CONFIGURED_SECRET:
    SECRET_KEY = _CONFIGURED_SECRET
else:
    # Ephemeral cryptographically random secret when not explicitly provided
    # Prevents default secret forgery (CWE-798 / SEC-017)
    SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

security = HTTPBearer(auto_error=False)

# --- IN-MEMORY BRUTE-FORCE LOCKOUT TRACKER ---
# Tracks failed attempts per identifier (IP or username/email)
# Structure: {identifier: [timestamp1, timestamp2, ...]}
_FAILED_ATTEMPTS: Dict[str, List[float]] = {}
_LOCKOUTS: Dict[str, float] = {}

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes

def get_client_ip(request: Request) -> str:
    # Check standard reverse proxy headers
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

def check_login_lockout(identifier: str):
    now = time.time()
    if identifier in _LOCKOUTS:
        locked_until = _LOCKOUTS[identifier]
        if now < locked_until:
            retry_after = int(locked_until - now) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Account temporarily locked for {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        else:
            del _LOCKOUTS[identifier]
            _FAILED_ATTEMPTS.pop(identifier, None)

def record_login_failure(identifier: str):
    now = time.time()
    window_start = now - LOCKOUT_DURATION_SECONDS
    attempts = [t for t in _FAILED_ATTEMPTS.get(identifier, []) if t > window_start]
    attempts.append(now)
    _FAILED_ATTEMPTS[identifier] = attempts

    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        _LOCKOUTS[identifier] = now + LOCKOUT_DURATION_SECONDS
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Account temporarily locked for 15 minutes.",
            headers={"Retry-After": str(LOCKOUT_DURATION_SECONDS)}
        )

def record_login_success(identifier: str):
    _FAILED_ATTEMPTS.pop(identifier, None)
    _LOCKOUTS.pop(identifier, None)

# --- SALTED PBKDF2-HMAC-SHA256 PASSWORD HASHING ---
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    ).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${derived}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False

    # Check for PBKDF2 format
    if hashed_password.startswith("pbkdf2:sha256:"):
        try:
            parts = hashed_password.split("$")
            if len(parts) == 3:
                algo_iter, salt, expected_hash = parts
                iterations = int(algo_iter.split(":")[2])
                calculated = hashlib.pbkdf2_hmac(
                    "sha256",
                    plain_password.encode("utf-8"),
                    salt.encode("utf-8"),
                    iterations
                ).hex()
                return hmac.compare_digest(calculated, expected_hash)
        except Exception:
            return False

    # Fallback to legacy SHA-256 with static salt for backwards compatibility
    legacy_salt = "flattrack_austin_tx_salt_2026"
    legacy_hash = hashlib.sha256((legacy_salt + plain_password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_hash, hashed_password)

# --- JWT CREATION & RBAC DECORATORS ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_claims(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> dict:
    # 1. Bearer token in Authorization header
    token = None
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif credentials and hasattr(credentials, "credentials") and credentials.credentials:
        token = credentials.credentials
    
    # 2. Check HttpOnly cookie
    if not token:
        token = request.cookies.get("flattrack_access_token")

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token."
            )

    # 3. No fallback PIN bypass allowed (Hardened Production RBAC)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials required. Please provide a valid Bearer token."
    )

def require_role(*allowed_roles: str):
    def role_checker(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
    ) -> dict:
        claims = get_current_user_claims(request, credentials)
        user_role = claims.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of {allowed_roles} role(s)"
            )
        return claims
    return role_checker

require_admin = require_role("admin")
require_staff = require_role("admin", "barista")
