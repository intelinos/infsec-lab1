from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, security
from .database import get_db
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", summary="Register a new user", response_model=dict)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка уникальности username
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Проверка уникальности email
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"msg": "user created", "username": db_user.username, "email": db_user.email}


@router.post("/login", summary="Obtain JWT token", response_model=schemas.TokenResponse)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_req.username).first()
    if not user or not security.verify_password(login_req.password, user.hashed_password):
        # Broken authentication -> respond with 401, do not leak which field was wrong
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expire = security.create_access_token(subject=user.username)
    return {"token": f"Bearer {token}", "expiresAt": expire}
