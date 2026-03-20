"""Initial schema — products, stores, inventory, shipments.

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

NOTE: Schema is managed in db/schema.sql for the initial seed.
This migration is a no-op placeholder so Alembic tracks baseline state.
Future schema changes go in new revision files.
"""
from alembic import op

revision      = '0001'
down_revision = None
branch_labels = None
depends_on    = None


def upgrade() -> None:
    # Baseline — schema already created by db/schema.sql seed script.
    # Future: op.create_table(...) or op.add_column(...)
    pass


def downgrade() -> None:
    pass
