"""map database learning objectives to RAG objectives"""
from alembic import op
from sqlalchemy import text


revision = "0007_rag_obj_id"
down_revision = "0006_fix_pass_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        ALTER TABLE learning_objectives
        ADD COLUMN IF NOT EXISTS rag_objective_id VARCHAR(150) NULL
    """))
    op.execute(text("""
        UPDATE learning_objectives
        SET rag_objective_id = CASE title
            WHEN '확률·통계의 기초' THEN 'stats.probability_foundations'
            WHEN '가설검정과 불확실성' THEN 'stats.hypothesis_uncertainty'
            WHEN 'ANOVA와 가정 위반 대안' THEN 'stats.anova_alternatives'
            WHEN '회귀분석과 진단' THEN 'stats.regression_diagnostics'
        END
        WHERE lecture_id = 'basic_statistics'
          AND level = 'parent'
    """))
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_learning_objectives_rag_objective_id
        ON learning_objectives (rag_objective_id)
    """))


def downgrade() -> None:
    op.execute(text("DROP INDEX IF EXISTS ix_learning_objectives_rag_objective_id"))
    op.execute(text("ALTER TABLE learning_objectives DROP COLUMN rag_objective_id"))
