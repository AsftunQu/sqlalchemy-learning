from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskService:

    @staticmethod
    def create_task(db: Session, user_id: int, task_data: TaskCreate) -> Task:
        """为指定用户创建任务"""
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,          # 关键:关联到当前登录用户
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
