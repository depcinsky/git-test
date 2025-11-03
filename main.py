from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import Base, engine
from models import User
from schemas import LoginData, UserCreate, UserOut
from crud import create_user, validate_user_credentials
from security import create_access_token
from deps import get_db, get_current_payload, get_current_username, require_roles

app = FastAPI(title="Auth App — JWT with roles")

# Inicjalizacja bazy (SQLite)
Base.metadata.create_all(bind=engine)

@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = validate_user_credentials(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    roles = [r.strip() for r in user.roles.split(",") if r.strip()]
    token = create_access_token(subject=user.username, roles=roles)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users", response_model=UserOut, dependencies=[Depends(require_roles("ROLE_ADMIN"))])
def add_user(payload: UserCreate, db: Session = Depends(get_db)):
    roles = payload.roles or ["ROLE_USER"]
    try:
        user = create_user(db, payload.username, payload.password, roles)
        return UserOut(id=user.id, username=user.username, roles=[r.strip() for r in user.roles.split(",") if r.strip()])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user_details")
def user_details(payload: dict = Depends(get_current_payload)):
    # Zwracamy cały payload JWT
    return {"payload": payload}

@app.get("/protected")
def protected_route(username: str = Depends(get_current_username)):
    return {"message": f"Hello {username}, this is a protected resource."}
