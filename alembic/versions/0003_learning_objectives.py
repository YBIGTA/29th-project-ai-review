"""add hierarchical learning objectives to study sessions"""
from alembic import op
from sqlalchemy import text


revision = "0003_learning_objectives"
down_revision = "0002_google_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        CREATE TABLE IF NOT EXISTS learning_objectives (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lecture_id VARCHAR(100) NOT NULL,
            parent_id UUID NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            level VARCHAR(10) NOT NULL,
            importance INTEGER NOT NULL DEFAULT 3,
            display_order INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_learning_objectives_level
                CHECK (level IN ('parent', 'child')),
            CONSTRAINT ck_learning_objectives_importance
                CHECK (importance BETWEEN 1 AND 5),
            CONSTRAINT fk_learning_objectives_parent
                FOREIGN KEY (parent_id) REFERENCES learning_objectives(id)
                ON DELETE CASCADE
        )
    """))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_learning_objectives_lecture_id ON learning_objectives (lecture_id)"))
    op.execute(text("""
        ALTER TABLE study_sessions
        ADD COLUMN IF NOT EXISTS learning_objective_id UUID NULL
        REFERENCES learning_objectives(id) ON DELETE RESTRICT
    """))
    op.execute(text("""
        ALTER TABLE study_sessions DROP CONSTRAINT IF EXISTS study_sessions_pass_status_check
    """))
    op.execute(text("""
        ALTER TABLE study_sessions
        ADD CONSTRAINT study_sessions_pass_status_check
        CHECK (pass_status IN ('IN_PROGRESS', 'P', 'NP'))
    """))


def downgrade() -> None:
    op.execute(text("ALTER TABLE study_sessions DROP COLUMN IF EXISTS learning_objective_id"))
    op.execute(text("DROP TABLE IF EXISTS learning_objectives CASCADE"))
