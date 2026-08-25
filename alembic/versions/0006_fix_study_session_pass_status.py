"""fix pass status column size and duplicate legacy constraint"""
from alembic import op
from sqlalchemy import text


revision = "0006_fix_pass_status"
down_revision = "0005_align_evaluation_scores"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        ALTER TABLE study_sessions
        DROP CONSTRAINT IF EXISTS chk_study_sessions_pass_status,
        ALTER COLUMN pass_status TYPE VARCHAR(20)
    """))


def downgrade() -> None:
    op.execute(text("""
        ALTER TABLE study_sessions
        ALTER COLUMN pass_status TYPE VARCHAR(2),
        ADD CONSTRAINT chk_study_sessions_pass_status
        CHECK (pass_status IN ('P', 'NP'))
    """))
