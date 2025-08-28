# utils/security.py
from fastapi import Request, Depends, HTTPException
from sqlmodel import Session, select, or_
from src.common.models import User
import src.common.schemes as schemes
from src.common.db_storage import get_session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User | None:
    """ 
    Get the currently logged-in user from the session 
    """

    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def login_user(request: Request, db_session: Session, username: str, password: str) -> User | None:
    """
    Fetch user by username or email
    """

    q = select(User).where(or_(User.email == username.strip().lower(), User.username == username))
    user = db_session.exec(q).first()

    if user is None or not verify_password(password, user.password):
        return None
    
    return user


def register_user(request: Request, db_session: Session, username: str, email: str, password: str) -> User:
    """
    Register a new user
    """

    q = select(User).where(or_(User.email == email.strip().lower(), User.username == username))
    existing_user = db_session.exec(q).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=username,
        email=email,
        password=hash_password(password)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user