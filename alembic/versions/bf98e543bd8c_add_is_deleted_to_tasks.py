"""add is_deleted to tasks

Revision ID: bf98e543bd8c
Revises: 20ec57f35226
Create Date: 2026-09-11 23:32:49.950845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf98e543bd8c'
down_revision: Union[str, Sequence[str], None] = '20ec57f35226'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. 新增软删除标记列;server_default 让已有数据自动补 false,避免 NOT NULL 报错
    op.add_column(
        'tasks',
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )
    # 2. 顺带把外键 ondelete 对齐为 CASCADE,消除 model 与数据库的 drift
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(None, 'tasks', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.create_foreign_key('tasks_user_id_fkey', 'tasks', 'users', ['user_id'], ['id'])
    op.drop_column('tasks', 'is_deleted')
