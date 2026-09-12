from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.logger import app_logger


class TaskService:

    @staticmethod
    def create_task(db: Session, user_id: int, task_data: TaskCreate) -> Task:
        """为指定用户创建任务"""
        app_logger.debug(f"开始创建任务: user_id={user_id}, title={task_data.title}")
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,          # 关键:关联到当前登录用户
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        app_logger.info(f"任务创建成功: ID={new_task.id}, user_id={user_id}")
        return new_task

    # 获取任务
    @staticmethod
    def get_tasks(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        is_completed: bool | None = None,
    ):
        """分页查询当前用户的任务列表，支持按完成状态筛选"""
        app_logger.debug(
            f"查询任务列表: user_id={user_id}, page={page}, page_size={page_size}, is_completed={is_completed}"
        )
        # 关键：只查询当前用户自己的任务（防止越权）
        query = db.query(Task).filter(Task.user_id == user_id, Task.is_deleted == False)

        # 状态筛选：None=全部， True=已完成， False=未完成
        if is_completed is not None:
            query = query.filter(Task.is_completed == is_completed)

        total = query.count()  # 先算总条数

        items = (
            query
            .order_by(Task.created_at.desc())  # 最新的排前面
            .offset((page-1) * page_size)  # 跳过前（page-1）页
            .limit(page_size)  # 只取当前页
            .all()
        )
        app_logger.debug(f"任务列表查询完成: 共 {total} 条, 本页返回 {len(items)} 条")
        return items, total

    @staticmethod 
    def get_task(db:Session, user_id:int, task_id:int) -> Task | None:
        """查询单任务，限定当前用户(查不到别人的任务)"""
        task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False)
            .first()
        )
        if task:
            app_logger.debug(f"查询任务详情成功: task_id={task_id}, user_id={user_id}")
        else:
            app_logger.debug(f"任务不存在或无权访问: task_id={task_id}, user_id={user_id}")
        return task

    # 新增更新方法
    @staticmethod
    def update_task(db: Session, user_id: int, task_id: int, task_data: TaskUpdate) -> Task | None:
        """更新任务(只更新传入的字段),返回 None 表示任务不存在"""
        task = db.query(Task).filter(
            Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False
        ).first()
        if task is None:
            app_logger.debug(f"更新失败,任务不存在: task_id={task_id}, user_id={user_id}")
            return None

        # exclude_unset=True:只取调用方真正传了的字段,没传的跳过
        update_data = task_data.model_dump(exclude_unset=True)
        app_logger.debug(f"更新任务字段: task_id={task_id}, data={update_data}")
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)
        app_logger.info(f"任务更新成功: ID={task_id}, user_id={user_id}")
        return task

    # 新增软删除方法
    @staticmethod
    def soft_delete_task(db:Session, user_id:int, task_id:int) -> bool:
        """软删除：把is_deleted设置为True，数据仍在表中"""
        app_logger.debug(f"开始软删除任务: task_id={task_id}, user_id={user_id}")
        task = db.query(Task).filter(
            Task.id==task_id, Task.user_id==user_id, Task.is_deleted==False
        ).first()
        if task is None:
            app_logger.debug(f"软删除失败,任务不存在: task_id={task_id}, user_id={user_id}")
            return False
        task.is_deleted = True
        db.commit()
        app_logger.info(f"任务已软删除: ID={task_id}, user_id={user_id}")
        return True
