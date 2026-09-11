import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.config import settings

def setup_logger(name: str = "sqlalchemy_app"):
    """
    配置应用日志系统
    """
    # 创建 logger
    logger = logging.getLogger(name)
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    logger.setLevel(log_level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ===== 控制台输出 =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ===== 文件输出（带轮转） =====
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 主要日志文件
    log_filename = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误日志单独文件
    error_log_filename = f"{log_dir}/error_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = RotatingFileHandler(
        error_log_filename,
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"日志系统初始化完成，日志级别: {settings.LOG_LEVEL}")
    return logger

# 创建全局 logger 实例
app_logger = setup_logger("sqlalchemy_learning")