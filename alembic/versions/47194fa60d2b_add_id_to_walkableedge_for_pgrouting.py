"""add id to WalkableEdge for pgrouting

Revision ID: 47194fa60d2b
Revises: 10a3b712bdeb
Create Date: 2025-05-04 01:42:26.977289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47194fa60d2b'
down_revision: Union[str, None] = '10a3b712bdeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
