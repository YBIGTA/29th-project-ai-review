"""replace Kakao user identifier with Google subject"""
from alembic import op
from sqlalchemy import text

revision = "0002_google_auth"
down_revision = "0001_initial_user_progress"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'kakao_user_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'google_user_id'
            ) THEN
                ALTER TABLE users RENAME COLUMN kakao_user_id TO google_user_id;
                ALTER TABLE users ALTER COLUMN google_user_id TYPE VARCHAR(255);
            END IF;
        END $$;
    """))


def downgrade() -> None:
    op.execute(text("ALTER TABLE users RENAME COLUMN google_user_id TO kakao_user_id"))
