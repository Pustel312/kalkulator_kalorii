"""remove old product name unique

Revision ID: 60c1efa5deda
Revises: 9f78c2b9c49d
Create Date: 2026-09-09 05:35:09.554457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60c1efa5deda'
down_revision: Union[str, Sequence[str], None] = '9f78c2b9c49d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_products_name",
        "products",
        type_="unique"
    )

def downgrade() -> None:
    op.create_unique_constraint(
        "uq_products_name",
        "products",
        ["name"]
    )