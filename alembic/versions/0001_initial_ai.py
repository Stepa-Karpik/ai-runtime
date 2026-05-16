from alembic import op
import sqlalchemy as sa
revision='0001_initial_ai'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
 op.create_table('ai_jobs',sa.Column('id',sa.String(64),primary_key=True),sa.Column('document_id',sa.String(64),nullable=False),sa.Column('content_ref',sa.String(128),nullable=False),sa.Column('status',sa.String(32),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False)); op.create_index('ix_ai_jobs_document_id','ai_jobs',['document_id'])
def downgrade(): op.drop_index('ix_ai_jobs_document_id',table_name='ai_jobs'); op.drop_table('ai_jobs')
