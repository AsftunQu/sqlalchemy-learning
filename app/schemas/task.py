from pydantic import BaseModel
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 分页包装模型

class TaskListResponse(BaseModel):
    """任务列表分页相应"""
    items: list[TaskResponse]  # 当前页的任务列表
    total: int  # 符合条件的总条数（不是当前页条数）
    page: int  # 当前页码
    page_size: int  # 每页数量


# 更新任务
class TaskUpdate(BaseModel):
    """更新任务，所有字段可选（只更新传入的字段）"""
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
