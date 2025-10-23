from sqlalchemy.future import select
from app.models.user import User
from app.models.database import get_db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Hash a senha fornecida usando bcrypt.
    
    Args:
        password (str): A senha em texto plano a ser hashada.
    Returns:
        str: A senha hashada.
    Raises:
        ValueError: Se a senha não for uma string ou tiver mais de 72 caracteres.
    """
    if not isinstance(password, str):
        raise ValueError(f"A senha recebida não é string, e sim {type(password)}")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("A senha não pode ter mais de 72 caracteres.")

    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verifica se a senha em texto plano corresponde à senha hashada.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Cria um token de acesso JWT.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def create_user(db, username: str, password: str):
    """Cria um novo usuário com a senha hashada.
    """
    hashed = hash_password(password)
    user = User(username=username, password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
