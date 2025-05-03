"""add pgrouting extension + routable edge view

Revision ID: 7c65dfdcafcc
Revises: 32113172727b
Create Date: 2025-05-02 01:14:47.951259

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '7c65dfdcafcc'
down_revision: Union[str, None] = '32113172727b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(text("CREATE EXTENSION IF NOT EXISTS pgrouting;"))
    op.execute(text("""
        CREATE VIEW routeable_edges AS
        SELECT row_number() OVER () AS id, 
                    u AS source, 
                    v AS target, 
                    length_m AS cost, 
                    length_m AS reverse_cost
        FROM walkable_edges;
        """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("DROP VIEW IF EXISTS routable_edges;"))
    op.execute(text("DROP EXTENSION IF EXISTS pgrouting;"))
