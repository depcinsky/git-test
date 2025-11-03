from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from models import User
from security import get_password_hash, verify_password

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, username: str, password: str, roles: List[str]) -> User:
    if get_user_by_username(db, username):
        raise ValueError("User already exists")
    user = User(username=username, password_hash=get_password_hash(password), roles=",".join(roles))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def validate_user_credentials(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user
    return None
