"""add jwt_refresh_token

Revision ID: 1e99042379d8
Revises: 23be1c38ecbe
Create Date: 2025-05-24 01:08:03.299864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '1e99042379d8'
down_revision: Union[str, None] = '23be1c38ecbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'accounts',
        'refresh_token',
        new_column_name='kakao_refresh_token',
        type_=sa.String(length=512),
        existing_type=sa.String(length=512),
        existing_nullable=True
    )
    op.add_column('accounts', sa.Column('jwt_refresh_token', sa.String(length=512), nullable=True))

def downgrade() -> None:
    op.drop_column('accounts', 'jwt_refresh_token')
    op.alter_column(
        'accounts',
        'kakao_refresh_token',
        new_column_name='refresh_token',
        type_=sa.String(length=512),
        existing_type=sa.String(length=512),
        existing_nullable=True
    )

