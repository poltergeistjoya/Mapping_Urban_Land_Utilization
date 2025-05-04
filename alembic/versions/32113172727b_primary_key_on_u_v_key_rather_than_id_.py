"""primary key on u,v,key rather than id in walkable_edges

Revision ID: 32113172727b
Revises: 2aa19f7f077d
Create Date: 2025-04-27 16:06:26.814697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32113172727b'
down_revision: Union[str, None] = '2aa19f7f077d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("walkable_edges", sa.Column("id", sa.Integer(), autoincrement=True, unique=True))
    op.create_index("idx_walkable_edges_id", "walkable_edges", ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_walkable_edges_id", table_name="walkable_edges")
    op.drop_column("walkable_edges", "id")
