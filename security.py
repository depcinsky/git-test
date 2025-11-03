import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Any

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")  # na produkcji tylko z ENV

def get_password_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))

def create_access_token(subject: str, roles: List[str], expires_delta: timedelta = timedelta(hours=1)) -> str:
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
