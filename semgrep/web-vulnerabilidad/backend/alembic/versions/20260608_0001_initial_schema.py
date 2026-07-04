"""initial schema

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260608_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("target_url", sa.String(length=2048), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("modules", sa.JSON(), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("timeout", sa.Integer(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scans_id"), "scans", ["id"], unique=False)
    op.create_index(op.f("ix_scans_user_id"), "scans", ["user_id"], unique=False)

    op.create_table(
        "vulnerabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=24), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("remediation", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("parameter", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vulnerabilities_id"), "vulnerabilities", ["id"], unique=False)
    op.create_index(op.f("ix_vulnerabilities_scan_id"), "vulnerabilities", ["scan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_vulnerabilities_scan_id"), table_name="vulnerabilities")
    op.drop_index(op.f("ix_vulnerabilities_id"), table_name="vulnerabilities")
    op.drop_table("vulnerabilities")
    op.drop_index(op.f("ix_scans_user_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_id"), table_name="scans")
    op.drop_table("scans")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

