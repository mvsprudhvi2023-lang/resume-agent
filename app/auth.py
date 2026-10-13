import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
TOKEN_MINUTES = 30

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing. Add it to your .env file.")


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Demo users. Passwords come from .env, never from the code.
USERS = {}
for name, role, env_key in [
    ("admin", "admin", "ADMIN_PASSWORD"),
    ("analyst", "user", "USER_PASSWORD"),
]:
    password = os.getenv(env_key)
    if password:
        USERS[name] = {"username": name, "role": role, "password_hash": _hash(password)}


def authenticate(username: str, password: str):
    user = USERS.get(username)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None
    return user


def create_token(user: dict) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    payload = {"sub": user["username"], "role": user["role"], "exp": expires}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = USERS.get(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user