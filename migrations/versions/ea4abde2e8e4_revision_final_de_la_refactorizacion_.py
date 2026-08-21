"""revision final de la refactorizacion pasada

Revision ID: ea4abde2e8e4
Revises: 6acc2a8a5eaf
Create Date: 2026-08-14 22:52:58.940544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea4abde2e8e4'
down_revision: Union[str, Sequence[str], None] = '6acc2a8a5eaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass