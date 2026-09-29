"""Align schema with models: NOT NULL timestamps, unique indexes on email / external_id.

Revision ID: 002
Revises: 001
Create Date: 2026-09-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ["users", "people", "relationships", "events", "sources", "media"]
TIMESTAMPS = ["created_at", "updated_at"]
UNIQUE_INDEXES = [("users", "ix_users_email", "email"), ("people", "ix_people_external_id", "external_id")]


def _set_timestamps_nullable(nullable: bool) -> None:
    for table in TABLES:
        if not nullable:
            for col in TIMESTAMPS:
                op.execute(f"UPDATE {table} SET {col} = CURRENT_TIMESTAMP WHERE {col} IS NULL")
        # batch mode rebuilds the table on SQLite (no ALTER COLUMN) and is a plain ALTER elsewhere
        with op.batch_alter_table(table) as batch:
            for col in TIMESTAMPS:
                batch.alter_column(
                    col,
                    existing_type=sa.DateTime(timezone=True),
                    existing_server_default=sa.func.now(),
                    nullable=nullable,
                )


def _set_indexes_unique(unique: bool) -> None:
    for table, name, column in UNIQUE_INDEXES:
        op.drop_index(name, table_name=table)
        op.create_index(name, table, [column], unique=unique)


def upgrade() -> None:
    _set_timestamps_nullable(False)
    _set_indexes_unique(True)


def downgrade() -> None:
    _set_indexes_unique(False)
    _set_timestamps_nullable(True)
