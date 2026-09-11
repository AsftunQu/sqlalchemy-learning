import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    # 数据库配置(从环境变量注入,不再硬编码密码)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    # 优先使用完整 DATABASE_URL,否则用独立变量拼装(密码做 URL 编码)
    DATABASE_URL = os.getenv("DATABASE_URL") or (
        f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        if all([DB_USER, DB_PASSWORD, DB_NAME])
        else None
    )

    # 应用配置
    APP_NAME = "SQLAlchemy Learning API"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_MAX_BYTES = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))  # 10MB
    LOG_FILE_BACKUP_COUNT = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    # JWT 配置(强制从环境变量读取,不再提供弱默认值)
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()

# 启动即校验关键配置,缺失则直接报错,避免静默降级到弱密钥/错误连接
if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY 未配置:请在 .env 中设置一个随机强密钥")
if not settings.DATABASE_URL:
    raise RuntimeError("数据库配置缺失:请在 .env 中设置 DATABASE_URL 或 DB_USER/DB_PASSWORD/DB_NAME")
