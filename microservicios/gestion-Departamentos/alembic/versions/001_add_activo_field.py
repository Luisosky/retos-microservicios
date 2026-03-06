"""Add activo field to Departamentos table

Revision ID: 001_add_activo_field
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_activo_field'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add activo column to Departamentos table."""
    op.add_column('Departamentos', sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    """Remove activo column from Departamentos table."""
    op.drop_column('Departamentos', 'activo')
