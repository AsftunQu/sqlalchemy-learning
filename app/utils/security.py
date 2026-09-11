from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成JWT，data里放payload(如{"sub":username})"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """解析并校验JWT，失败会抛JWTError"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])