"""Add audio transcript and analysis fields to Evidence model

Revision ID: 6aaf07275b8f
Revises: 522f6e479acf
Create Date: 2025-05-10 20:12:59.152327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6aaf07275b8f'
down_revision = '522f6e479acf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('transcript', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('transcript_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('transcript_analysis', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('analysis_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('processed_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('evidence', schema=None) as batch_op:
        batch_op.drop_column('processed_at')
        batch_op.drop_column('analysis_status')
        batch_op.drop_column('transcript_analysis')
        batch_op.drop_column('transcript_status')
        batch_op.drop_column('transcript')

    # ### end Alembic commands ###
