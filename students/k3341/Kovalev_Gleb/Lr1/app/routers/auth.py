from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import create_access_token, hash_password, verify_password
from app.db import get_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import PasswordChange, Token, UserCreate, UserLogin, UserRead, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)) -> UserResponse:
    existing_user = session.exec(
        select(User).where((User.username == user.username) | (User.email == user.email))
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"status": 200, "data": db_user}


@router.post("/login", response_model=Token)
def login(user: UserLogin, session: Session = Depends(get_session)) -> Token:
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return Token(access_token=create_access_token(db_user.id), token_type="bearer")


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/users", response_model=List[UserRead])
def users_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[User]:
    return session.exec(select(User)).all()


@router.patch("/change_password")
def change_password(
    password_data: PasswordChange,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = hash_password(password_data.new_password)
    session.add(current_user)
    session.commit()
    return {"ok": True}
