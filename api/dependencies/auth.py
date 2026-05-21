# api/dependencies/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# 配置（生产环境应从 .env 读取）
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# 模拟用户数据库（实际项目应使用 PostgreSQL）
fake_users_db = {
    "zhangwei": {
        "username": "zhangwei",
        "full_name": "张伟",
        "email": "zhangwei@starring.com",
        "department": "销售部",
        "hashed_password": pwd_context.hash("20030730"),
    },
    "lina": {
        "username": "lina",
        "full_name": "李娜",
        "email": "lina@starring.com",
        "department": "销售部",
        "hashed_password": pwd_context.hash("secret123"),
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    department: Optional[str] = None

class User(BaseModel):
    username: str
    full_name: str
    email: str
    department: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, db[username]["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user