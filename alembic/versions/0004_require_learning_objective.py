"""require a selected learning objective for every study session"""
from alembic import op
from sqlalchemy import text


revision = "0004_require_learning_objective"
down_revision = "0003_learning_objectives"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing local progress is disposable for this schema transition.
    op.execute(text("""
        TRUNCATE TABLE
            evaluations,
            transcriptions,
            audio_files,
            study_sessions,
            auth_sessions,
            users,
            learning_objectives
        RESTART IDENTITY CASCADE
    """))
    op.execute(text("""
        ALTER TABLE study_sessions
        ALTER COLUMN learning_objective_id SET NOT NULL
    """))
    op.execute(text("""
        ALTER TABLE study_sessions
        ALTER COLUMN pass_status SET DEFAULT 'IN_PROGRESS'
    """))


def downgrade() -> None:
    op.execute(text("""
        ALTER TABLE study_sessions
        ALTER COLUMN learning_objective_id DROP NOT NULL
    """))
    op.execute(text("""
        ALTER TABLE study_sessions
        ALTER COLUMN pass_status SET DEFAULT 'NP'
    """))
