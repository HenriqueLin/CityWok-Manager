"""order model

Revision ID: df067cb57c4a
Revises: 31abbbb774c0
Create Date: 2021-07-01 17:03:35.652147

"""
import citywok_ms
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df067cb57c4a"
down_revision = "31abbbb774c0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("value", citywok_ms.utils.models.SqliteDecimal(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order")),
    )
    with op.batch_alter_table("file", schema=None) as batch_op:
        batch_op.add_column(sa.Column("order_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_file_order_id_order"), "order", ["order_id"], ["id"]
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("file", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_file_order_id_order"), type_="foreignkey"
        )
        batch_op.drop_column("order_id")

    op.drop_table("order")
    # ### end Alembic commands ###
