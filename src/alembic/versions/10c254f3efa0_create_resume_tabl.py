"""create resume tabl

Revision ID: 10c254f3efa0
Revises: 
Create Date: 2024-11-08 16:33:11.447618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10c254f3efa0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resume',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('lastname', sa.String(length=512), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_resume'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resume')
    # ### end Alembic commands ###
