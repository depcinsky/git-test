from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import List, Dict, Any
from security import decode_token
from models import User

bearer = HTTPBearer(auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_payload(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

def get_current_username(payload: Dict[str, Any] = Depends(get_current_payload)) -> str:
    return str(payload.get("sub"))

def get_current_roles(payload: Dict[str, Any] = Depends(get_current_payload)) -> List[str]:
    roles = payload.get("roles") or []
    if not isinstance(roles, list):
        roles = [r.strip() for r in str(roles).split(",") if r.strip()]
    return roles

def require_roles(*required: str):
    def checker(roles: List[str] = Depends(get_current_roles)):
        if not any(r in roles for r in required):
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
    return checker
