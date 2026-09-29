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


def _set_legacy_unique_constraints(present: bool) -> None:
    """001 also made these columns unique via constraints; the unique indexes now cover that.

    Postgres names them <table>_<column>_key. SQLite's are unnamed and part of the table
    definition, so they can't be dropped by name (and autogenerate doesn't report them there).
    """
    if op.get_bind().dialect.name != "postgresql":
        return
    for table, _, column in UNIQUE_INDEXES:
        name = f"{table}_{column}_key"
        if present:
            op.create_unique_constraint(name, table, [column])
        else:
            op.drop_constraint(name, table, type_="unique")


def upgrade() -> None:
    _set_timestamps_nullable(False)
    _set_indexes_unique(True)
    _set_legacy_unique_constraints(False)


def downgrade() -> None:
    _set_legacy_unique_constraints(True)
    _set_indexes_unique(False)
    _set_timestamps_nullable(True)
