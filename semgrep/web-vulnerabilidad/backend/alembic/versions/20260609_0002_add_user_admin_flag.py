"""add user admin flag

Revision ID: 20260609_0002
Revises: 20260608_0001
Create Date: 2026-06-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260609_0002"
down_revision: str | None = "20260608_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), server_default=sa.text("0"), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_admin")
