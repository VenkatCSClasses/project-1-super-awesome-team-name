"""merge multiple heads

Revision ID: 4c3b32cd197f
Revises: 8f7ad63f871b, cfe4ed0dac91
Create Date: 2026-02-26 01:16:14.027015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4c3b32cd197f'
down_revision: Union[str, Sequence[str], None] = ('8f7ad63f871b', 'cfe4ed0dac91')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
