# 这是整个鉴权的关键，后面任何接口只要写Depends(get_current_user)就能拿到当前登录用户
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import UserService
from app.utils.security import decode_access_token

# tokenUrl指向登录接口，Swagger文档的“Authorize”按钮会用到它
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(
        token:str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
):
    """从请求头解析JWT，返回当前登录的User对象；无效则401"""
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserService.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user