"""fix ChatMessage.created_at default to now

Revision ID: 4693f39b15bd
Revises: 6b9b4325395a
Create Date: 2025-05-11 02:51:51.246247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '4693f39b15bd'
down_revision: Union[str, None] = '6b9b4325395a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: set default timestamp on chat_messages.created_at."""
    with op.batch_alter_table("chat_messages") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema: remove default timestamp from chat_messages.created_at."""
    with op.batch_alter_table("chat_messages") as batch_op:
        batch_op.alter_column(
            "created_at",
            server_default=None,
            existing_type=sa.DateTime(),
            existing_nullable=False,
        )
