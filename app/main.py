from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.utils.logger import app_logger
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.hash import verify_password
from app.utils.security import create_access_token
from app.schemas.token import Token
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskUpdate
from app.services.task_service import TaskService

# 创建 FastAPI 应用
app = FastAPI(
    title="SQLAlchemy Learning API",
    description="学习 SQLAlchemy 和 FastAPI 的项目",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """应用启动时的日志"""
    app_logger.info("=" * 60)
    app_logger.info("SQLAlchemy Learning API 启动")
    app_logger.info(f"日志级别: {app_logger.level}")
    app_logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的日志"""
    app_logger.info("=" * 60)
    app_logger.info("SQLAlchemy Learning API 关闭")
    app_logger.info("=" * 60)

# 健康检查接口
@app.get("/health", tags=["System"])
async def health_check():
    """检查服务是否正常运行"""
    app_logger.info("健康检查被调用")
    return {"status": "healthy", "service": "sqlalchemy-learning"}

# 用户注册接口
@app.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名（3-50字符）
    - **email**: 有效的邮箱地址
    - **password**: 密码（至少8位）
    """
    try:
        app_logger.info(f"收到注册请求: username={user_data.username}, email={user_data.email}")
        
        # 调用服务层创建用户
        new_user = UserService.create_user(db, user_data)
        
        app_logger.info(f"用户注册成功: {user_data.username}, ID: {new_user.id}")
        return new_user
        
    except ValueError as e:
        app_logger.warning(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        app_logger.error(f"注册过程发生未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误，请稍后重试"
        )

# 登录接口：返回JWT
@app.post("/api/login", response_model=Token, tags=["Auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """用户+密码登录，成功返回access_token"""
    app_logger.info(f"收到登录请求: username={form_data.username}")
    user = UserService.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):  # bcrypt校验
        app_logger.warning(f"登录失败: username={form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误",
        )
    # sub=subject,通常放用户名或用户ID
    token = create_access_token(data = {"sub": user.username})  # 签发JWT
    app_logger.info(f"登录成功: username={user.username}, user_id={user.id}")
    return Token(access_token=token)

# 受保护接口示例
@app.get("/api/me",response_model=UserResponse, tags=["User"])
async def read_current_user(current_user: User = Depends(get_current_user)):
    app_logger.info(f"收到查询当前用户请求: username={current_user.username}, user_id={current_user.id}")
    return current_user

# 创建任务接口（仅登录用户可调用）
@app.post("/api/tasks", response_model = TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Task"])
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),  # 鉴权：未登录会直接401
    db: Session = Depends(get_db),
):
    """创建当前登录用户的任务"""
    app_logger.info(f"收到创建任务请求: user_id={current_user.id}, title={task_data.title}")
    return TaskService.create_task(db, current_user.id, task_data)

# 列表任务
@app.get("/api/tasks", response_model=TaskListResponse, tags=["Task"])
async def list_tasks(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_completed: bool | None = Query(None, description="状态筛选：不传=全部，true=已完成，false=未完成"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """分页查询当前登录用户的任务列表"""
    app_logger.info(f"收到任务列表请求: user_id={current_user.id}, page={page}, page_size={page_size}, is_completed={is_completed}")
    items, total = TaskService.get_tasks(
        db, current_user.id, page, page_size, is_completed
    )
    return TaskListResponse(items=items, total=total, page=page, page_size=page_size)

# 任务详情接口
@app.get("/api/tasks/{task_id}", response_model=TaskResponse, tags=["Task"])
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询单条任务详情（仅限本人任务）"""
    app_logger.info(f"收到任务详情请求: task_id={task_id}, user_id={current_user.id}")
    task = TaskService.get_task(db, current_user.id, task_id)
    if task is None:
        app_logger.warning(f"任务详情查询失败: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    return task

# 更新任务
@app.patch("/api/tasks/{task_id}", response_model=TaskResponse, tags=["task"])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新任务，如把is_completed改成true标记完成"""
    app_logger.info(f"收到更新任务请求: task_id={task_id}, user_id={current_user.id}")
    task = TaskService.update_task(db, current_user.id, task_id, task_data)
    if task is None:
        app_logger.warning(f"更新任务失败: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return task

# 删除任务（软删除用DELETE）
@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Task"])
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """软删除任务（数据仍在数据库，只是标记is_deleted=true）"""
    app_logger.info(f"收到删除任务请求: task_id={task_id}, user_id={current_user.id}")
    success = TaskService.soft_delete_task(db, current_user.id, task_id)
    if not success:
        app_logger.warning(f"删除任务失败: task_id={task_id}, user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    return None  # 204无返回内容=删除成功