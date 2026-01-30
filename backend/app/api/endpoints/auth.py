from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security, database
from app.models.user import User
from app.schemas import user as user_schemas
from app.core.config import settings
from app.api import deps

router = APIRouter()

@router.post("/register", response_model=user_schemas.User)
def register(user_in: user_schemas.UserCreate, db: Session = Depends(database.get_db)) -> Any:
    user = db.query(User).filter(User.nickname == user_in.nickname).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this nickname already exists in the system.",
        )
    try:
        user = User(
            nickname=user_in.nickname,
            email=user_in.email,
            hashed_password=security.get_password_hash(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        print(f"Registration Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}",
        )

@router.post("/login", response_model=user_schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)) -> Any:
    # We use nickname as username in form_data
    user = db.query(User).filter(User.nickname == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect nickname or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.nickname}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schemas.User)
def read_users_me(current_user: User = Depends(deps.get_current_user)) -> Any:
    return current_user
