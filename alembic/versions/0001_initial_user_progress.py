"""create user progress tables"""
from alembic import op
from sqlalchemy import text

revision = "0001_initial_user_progress"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    with open("docs/user_progress_erd.sql", encoding="utf-8") as schema_file:
        op.execute(text(schema_file.read()))

def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS evaluations, transcriptions, audio_files, study_sessions, auth_sessions, users CASCADE"))
