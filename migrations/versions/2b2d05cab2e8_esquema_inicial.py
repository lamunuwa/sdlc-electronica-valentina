"""esquema inicial

Revision ID: 2b2d05cab2e8
Revises: 
Create Date: 2026-08-05 08:42:45.524547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2b2d05cab2e8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Crear tabla principal 'sensors'
    op.create_table(
        'sensors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('unit', sa.String(length=10), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('sensors_pkey'))
    )
    op.create_index(op.f('ix_sensors_name'), 'sensors', ['name'], unique=True)

    # 2. Crear tabla dependiente 'readings'
    op.create_table(
        'readings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sensor_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(precision=53), nullable=False),
        sa.Column('unit', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('hash_id', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ['sensor_id'], 
            ['sensors.id'], 
            name=op.f('readings_sensor_id_fkey'), 
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('readings_pkey')),
        sa.UniqueConstraint('sensor_id', 'hash_id', name=op.f('unique_hash'))
    )
    op.create_index(op.f('ix_readings_hash_id'), 'readings', ['hash_id'], unique=False)
    op.create_index(op.f('ix_reading_timestamp'), 'readings', ['sensor_id', 'timestamp'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Al revertir: eliminar primero la tabla dependiente 'readings', luego 'sensors'
    op.drop_index(op.f('ix_reading_timestamp'), table_name='readings')
    op.drop_index(op.f('ix_readings_hash_id'), table_name='readings')
    op.drop_table('readings')

    op.drop_index(op.f('ix_sensors_name'), table_name='sensors')
    op.drop_table('sensors')