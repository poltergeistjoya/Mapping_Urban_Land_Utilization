"""primary key to id on walkable_edges

Revision ID: 6982a2c7bde3
Revises: bc0843c859c4
Create Date: 2025-05-06 15:37:08.869354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6982a2c7bde3'
down_revision: Union[str, None] = 'bc0843c859c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing primary key constraint on (u, v, key)
    op.drop_constraint("walkable_edges_pkey", "walkable_edges", type_="primary")

    # Drop unique constraint on id (replace it with primary key)
    op.drop_constraint("walkable_edges_id_key", "walkable_edges", type_="unique")

    # Create new primary key on id
    op.create_primary_key("walkable_edges_pkey", "walkable_edges", ["id"])

    # Add unique constraint back on (u, v, key)
    op.create_unique_constraint("uq_u_v_key", "walkable_edges", ["u", "v", "key"])


def downgrade() -> None:
    # Drop the new primary key on id
    op.drop_constraint("walkable_edges_pkey", "walkable_edges", type_="primary")

    # Drop unique constraint on (u, v, key)
    op.drop_constraint("uq_u_v_key", "walkable_edges", type_="unique")

    # Recreate original primary key on (u, v, key)
    op.create_primary_key("walkable_edges_pkey", "walkable_edges", ["u", "v", "key"])

    # Recreate unique constraint on id
    op.create_unique_constraint("walkable_edges_id_key", "walkable_edges", ["id"])
