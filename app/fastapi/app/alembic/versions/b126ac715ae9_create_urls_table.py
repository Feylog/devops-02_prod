"""create urls table

The urls table stores shortened URLs. Schema decisions documented in
app/db/models.py. short_code is nullable to allow the two-step insert
pattern (INSERT row, then UPDATE with base62-encoded code), both
running in one transaction.

Revision ID: b126ac715ae9
Revises:
Create Date: 2026-05-23 12:34:16.370174

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b126ac715ae9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=True),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("click_count", sa.BigInteger(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_urls_short_code"), "urls", ["short_code"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_urls_short_code"), table_name="urls")
    op.drop_table("urls")
