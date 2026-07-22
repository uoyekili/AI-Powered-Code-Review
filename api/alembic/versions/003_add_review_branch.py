"""Add the reviewed Git branch.

Revision ID: 003
Revises: 002
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "reviews",
        sa.Column(
            "branch",
            sa.String(length=255),
            server_default="main",
            nullable=False,
        ),
    )
    op.alter_column("reviews", "branch", server_default=None)


def downgrade() -> None:
    op.drop_column("reviews", "branch")
