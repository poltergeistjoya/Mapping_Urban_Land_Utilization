"""Add unique constraint to places

Revision ID: 9e7b039b01c9
Revises: 47194fa60d2b
Create Date: 2025-05-04 23:02:42.685621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9e7b039b01c9'
down_revision: Union[str, None] = '47194fa60d2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint on name, place_type, geom in places."""
    op.create_unique_constraint(
        "uq_place_name_type_geom",
        "places",
        ["name", "place_type", "geom"]
    )


def downgrade() -> None:
    """Remove unique constraint from places."""
    op.drop_constraint(
        "uq_place_name_type_geom",
        "places",
        type_="unique"
    )
