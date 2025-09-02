# src/modules/auth_operations.py

from fastapi import Request, Depends, HTTPException
from sqlmodel import Session, select, or_
from passlib.context import CryptContext
from typing import Optional
from src.common.models import User
from src.common.db_storage import get_session
import src.common.schemes as schemes


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(request: Request, db_session: Session = Depends(get_session)) -> Optional[User]:
    """ 
    Get the currently logged-in user from the session 
    """

    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db_session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def login_user(request: Request, db_session: Session, user_data: schemes.LoginForm) -> User:
    """
    Fetch user by username or email
    """

    q = select(User).where(or_(User.email == user_data.username.strip().lower(), User.username == user_data.username))
    user = db_session.exec(q).first()

    if user is None or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return user


def register_user(request: Request, db_session: Session, user_data: schemes.RegisterForm) -> User:
    """
    Register a new user
    """

    if db_session.exec(select(User).where(User.username == user_data.username)).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    if db_session.exec(select(User).where(User.email == user_data.email.strip().lower())).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email.strip().lower(),
        password=hash_password(user_data.password)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user