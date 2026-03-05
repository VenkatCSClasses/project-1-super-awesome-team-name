import os
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
from argon2.exceptions import VerifyMismatchError
from argon2 import PasswordHasher
from sqlmodel import Session, select
from models import User
from database import engine

load_dotenv()
ph = PasswordHasher()
SECRET_KEY=os.getenv("SECRET_KEY", "placeholder_secret_key")
ALGORITHM="HS256"


def get_user_by_id(user_id: int):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        return user

def get_user_by_username(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        return user

def register_user(username: str, password: str) -> bool:
    if get_user_by_username(username) is not None:
        return False
    hashed_password = ph.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
    return True

def generate_login_token(user_id: int, permission: int) -> str:
    minutes_valid = os.getenv("TOKEN_LIFETIME_MINUTES", "60")
    expire = datetime.utcnow() + timedelta(minutes=int(minutes_valid))
    to_encode = {"user_id": user_id, "exp": expire, "permission": permission}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if user is None:
        return False

    try:
        ph.verify(user.hashed_password, password)
        return generate_login_token(user.id, user.permission)
        
    except VerifyMismatchError:
        return False

    return None


def ensure_root_user():
    """Ensure a root user exists with username 'root', password 'root', permission=2."""
    root = get_user_by_username("root")
    if root is not None:
        return False

    hashed_password = ph.hash("root")
    new_user = User(username="root", hashed_password=hashed_password, permission=2)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
    return True

