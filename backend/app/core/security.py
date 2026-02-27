from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from .config import Settings, get_settings
from ..repositories.user import UserRepository, UserRow


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict[str, Any], settings: Settings, expires_minutes: int = 60 * 24) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})
    secret = getattr(settings, "jwt_secret", None) or "dev-secret-change-me"
    algorithm = getattr(settings, "jwt_algorithm", "HS256")
    return jwt.encode(to_encode, secret, algorithm=algorithm)


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> UserRow:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        secret = getattr(settings, "jwt_secret", None) or "dev-secret-change-me"
        algorithm = getattr(settings, "jwt_algorithm", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        sub: Optional[str] = payload.get("sub")  # type: ignore[assignment]
        if sub is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo: UserRepository = request.app.state.user_repo  # type: ignore[attr-defined]
    user = await user_repo.get_by_id(sub)
    if user is None:
        raise credentials_exception
    return user

