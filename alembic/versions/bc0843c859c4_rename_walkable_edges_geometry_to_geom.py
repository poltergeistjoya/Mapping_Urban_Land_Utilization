"""rename walkable edges geometry to geom

Revision ID: bc0843c859c4
Revises: 9e7b039b01c9
Create Date: 2025-05-05 01:04:53.837886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bc0843c859c4'
down_revision: Union[str, None] = '9e7b039b01c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("walkable_edges", "geometry", new_column_name="geom")
    op.drop_index("idx_walkable_edges_geometry", table_name="walkable_edges")
    op.create_index("idx_walkable_edges_geom", "walkable_edges", ["geom"], postgresql_using="gist")


def downgrade():
    op.alter_column("walkable_edges", "geom", new_column_name="geometry")
    op.drop_index("idx_walkable_edges_geom", table_name="walkable_edges")
    op.create_index("idx_walkable_edges_geometry", "walkable_edges", ["geometry"], postgresql_using="gist")

