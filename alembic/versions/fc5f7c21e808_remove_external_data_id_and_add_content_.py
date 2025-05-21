"""remove external_data_id and add content_external_data M2M table

Revision ID: fc5f7c21e808
Revises: e6f2834fb450
Create Date: 2025-05-21 16:28:33.402851
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fc5f7c21e808'
down_revision: Union[str, None] = 'e6f2834fb450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 외래키 삭제 및 컬럼 제거
    op.drop_constraint('contents_ibfk_4', 'contents', type_='foreignkey')
    op.drop_column('contents', 'external_data_id')

    # 새 중간 테이블 생성 (Content <-> ExternalData M2M)
    op.create_table(
        'content_external_data',
        sa.Column('content_id', sa.BigInteger(), sa.ForeignKey('contents.content_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('external_data_id', sa.Integer(), sa.ForeignKey('external_data.external_data_id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 중간 테이블 제거
    op.drop_table('content_external_data')

    # 외래키 복구
    op.add_column('contents', sa.Column('external_data_id', sa.Integer(), nullable=True))
    op.create_foreign_key('contents_ibfk_4', 'contents', 'external_data', ['external_data_id'], ['external_data_id'])
