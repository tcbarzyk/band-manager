"""Sync with SQLAlchemy models

Revision ID: a08aea11a9bd
Revises: 
Create Date: 2025-10-07 00:46:47.073404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a08aea11a9bd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Since this is just to mark the current state as migrated,
    # we'll assume the database schema matches our models.
    # This migration essentially tells Alembic "we're starting from here"
    pass


def downgrade() -> None:
    pass
