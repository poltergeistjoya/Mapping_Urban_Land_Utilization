"""walkable_edges row can be found from routeable_edges

Revision ID: 10a3b712bdeb
Revises: 7c65dfdcafcc
Create Date: 2025-05-03 01:54:14.672463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '10a3b712bdeb'
down_revision: Union[str, None] = '7c65dfdcafcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(text("DROP VIEW IF EXISTS routable_edges;"))
    op.execute(text("""
        CREATE VIEW routable_edges AS
        SELECT
            u AS source,
            v AS target,
            key,
            length_m AS cost,
            length_m AS reverse_cost
        FROM walkable_edges;
    """))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("DROP VIEW IF EXISTS routable_edges;"))
    op.execute(text("""
        CREATE VIEW routable_edges AS
        SELECT
            row_number() OVER () AS id,
            u AS source,
            v AS target,
            length_m AS cost,
            length_m AS reverse_cost
        FROM walkable_edges;
    """))
