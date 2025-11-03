from pydantic import BaseModel, Field
from typing import List, Optional

class LoginData(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6)
    roles: Optional[List[str]] = None

class UserOut(BaseModel):
    id: int
    username: str
    roles: List[str]

    class Config:
        from_attributes = True
