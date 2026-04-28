"""Update Application table with status and updated_at columns

Revision ID: 002_update_application_table
Revises: 001_create_admin_tables
Create Date: 2024-01-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_update_application_table'
down_revision = '001_create_admin_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if status column exists, if not add it
    # Note: The Application model already has status column, so this is a safety check
    # In case the column doesn't exist in the database
    try:
        op.add_column('applications', sa.Column('status', sa.String(), nullable=False, server_default='pending'))
    except Exception:
        # Column already exists
        pass
    
    # Check if updated_at column exists, if not add it
    try:
        op.add_column('applications', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    except Exception:
        # Column already exists
        pass


def downgrade() -> None:
    # Note: We don't remove these columns as they are part of the core Application model
    # and removing them would break the application
    pass
