"""add product type to logs

Revision ID: a87a195bcb16
Revises: 7250c59396a1
Create Date: 2026-09-14 06:28:09.957958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a87a195bcb16'
down_revision: Union[str, Sequence[str], None] = '7250c59396a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


product_type_enum = sa.Enum(
    "ingredient",
    "product",
    "dish",
    name="product_type",
    create_type=False
)

def upgrade() -> None:
    op.add_column(
        "logs",
        sa.Column(
            "product_type",
            product_type_enum,
            nullable=False
        )
    )

def downgrade() -> None:
    op.drop_column("logs", "product_type")
