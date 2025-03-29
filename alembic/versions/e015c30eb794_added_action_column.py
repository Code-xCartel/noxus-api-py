"""Added Action Column

Revision ID: e015c30eb794
Revises: 1b89c5ba9692
Create Date: 2025-03-20 19:55:59.296891

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e015c30eb794"
down_revision: Union[str, None] = "1b89c5ba9692"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "friends", sa.Column("action_by", sa.String(length=15), nullable=True)
    )
    op.create_foreign_key(
        None, "friends", "users", ["action_by"], ["nox_id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "friends", type_="foreignkey")
    op.drop_column("friends", "action_by")
    # ### end Alembic commands ###
