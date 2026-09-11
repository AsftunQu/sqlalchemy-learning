import bcrypt
from app.utils.logger import app_logger

def hash_password(password: str) -> str:
    """
    使用 bcrypt 对密码进行哈希处理
    """
    try:
        app_logger.debug("开始哈希密码")
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        app_logger.debug("密码哈希成功")
        return hashed.decode('utf-8')
    except Exception as e:
        app_logger.error(f"密码哈希失败: {e}", exc_info=True)
        raise ValueError("密码加密失败")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    """
    try:
        app_logger.debug("开始验证密码")
        result = bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
        app_logger.debug(f"密码验证结果: {result}")
        return result
    except Exception as e:
        app_logger.error(f"密码验证失败: {e}", exc_info=True)
        return False