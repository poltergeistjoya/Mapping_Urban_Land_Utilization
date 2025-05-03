"""create locations and places table

Revision ID: 6adf0a590f6e
Revises: 7c65dfdcafcc
Create Date: 2025-05-02 03:50:36.690217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = '6adf0a590f6e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('location_type', sa.ARRAY(sa.String), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('parent_location_id', sa.Integer, sa.ForeignKey('locations.id'), nullable=True),
        sa.Column('geom', Geometry('MULTIPOLYGON', srid=4326), nullable=False)
    )

    op.create_table(
        'places',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('desc', sa.String),
        sa.Column('place_type', sa.String, nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('year_added', sa.Integer),
        sa.Column('year_removed', sa.Integer),
        sa.Column('location_id', sa.Integer, sa.ForeignKey('locations.id')),
        sa.Column('geom', Geometry('POINT', srid=4326), nullable=False)
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('places')
    op.drop_table('locations')
