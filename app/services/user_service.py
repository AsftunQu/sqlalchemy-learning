from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.hash import hash_password
from app.utils.logger import app_logger

class UserService:
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        创建新用户
        """
        app_logger.debug(f"开始创建用户: {user_data.username}")
        
        # 检查用户名或邮箱是否已存在
        app_logger.debug(f"检查用户名 '{user_data.username}' 和邮箱 '{user_data.email}' 是否存在")
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                app_logger.warning(f"用户名已被占用: {user_data.username}")
                raise ValueError(f"用户名 '{user_data.username}' 已被使用")
            else:
                app_logger.warning(f"邮箱已被注册: {user_data.email}")
                raise ValueError(f"邮箱 '{user_data.email}' 已被注册")
        
        # 创建新用户
        try:
            app_logger.debug("开始哈希密码")
            hashed_password = hash_password(user_data.password)
            app_logger.debug("密码哈希完成")
            
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password
            )
            
            app_logger.debug(f"用户对象创建成功，准备保存到数据库")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            app_logger.info(f"用户注册成功: {user_data.username} (ID: {new_user.id})")
            return new_user
            
        except IntegrityError as e:
            db.rollback()
            app_logger.error(f"数据库完整性错误: {e}")
            raise ValueError("注册失败，请稍后重试")
        except Exception as e:
            db.rollback()
            app_logger.error(f"创建用户失败: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """根据用户名获取用户"""
        app_logger.debug(f"查询用户: {username}")
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """根据邮箱获取用户"""
        app_logger.debug(f"查询用户邮箱: {email}")
        return db.query(User).filter(User.email == email).first()