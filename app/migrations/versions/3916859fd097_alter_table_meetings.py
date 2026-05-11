"""alter table meetings

Revision ID: 3916859fd097
Revises: 945988b261b1
Create Date: 2026-05-11 08:47:03.021927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = '3916859fd097'
down_revision: Union[str, Sequence[str], None] = '945988b261b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE certificationstatus AS ENUM ('planned', 'completed')")
    op.alter_column(
        "meetings",
        "status",
        existing_type=sa.VARCHAR(),
        type_=sa.Enum("planned", "completed", name="certificationstatus"),
        server_default="planned",
        existing_nullable=False,
        postgresql_using="status::text::certificationstatus",
    )
    op.execute("ALTER TABLE meetings ALTER COLUMN status SET DEFAULT 'planned'")


def downgrade() -> None:
    op.alter_column("meetings", "status", server_default=None)
    op.alter_column(
        "meetings",
        "status",
        existing_type=sa.Enum("planned", "completed", name="certificationstatus"),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="status::text",
    )
    op.execute("DROP TYPE certificationstatus")
