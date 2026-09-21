import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_FAILED_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


def get_lockout_seconds_remaining(user) -> int:
    if not user.locked_until:
        return 0

    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)

    remaining = (locked_until - datetime.now(timezone.utc)).total_seconds()
    return int(remaining) if remaining > 0 else 0

def register_failed_login(db, user) -> None:
    user.failed_attempts += 1
    if user.failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
    db.commit()


def reset_failed_login(db, user) -> None:
    user.failed_attempts = 0
    user.locked_until = None
    db.commit()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])