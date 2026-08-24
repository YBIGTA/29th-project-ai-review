"""align evaluation score columns with the 60-20-20 rubric"""
from alembic import op
from sqlalchemy import text


revision = "0005_align_evaluation_scores"
down_revision = "0004_require_learning_objective"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("ALTER TABLE evaluations RENAME COLUMN accuracy_score TO essential_score"))
    op.execute(text("ALTER TABLE evaluations RENAME COLUMN structural_score TO supporting_score"))
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_accuracy"))
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_coverage"))
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_structural"))
    op.execute(text("""
        ALTER TABLE evaluations
        ADD CONSTRAINT chk_evaluations_essential
        CHECK (essential_score BETWEEN 0 AND 60),
        ADD CONSTRAINT chk_evaluations_coverage
        CHECK (coverage_score BETWEEN 0 AND 20),
        ADD CONSTRAINT chk_evaluations_supporting
        CHECK (supporting_score BETWEEN 0 AND 20)
    """))


def downgrade() -> None:
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_essential"))
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_coverage"))
    op.execute(text("ALTER TABLE evaluations DROP CONSTRAINT chk_evaluations_supporting"))
    op.execute(text("ALTER TABLE evaluations RENAME COLUMN essential_score TO accuracy_score"))
    op.execute(text("ALTER TABLE evaluations RENAME COLUMN supporting_score TO structural_score"))
    op.execute(text("""
        ALTER TABLE evaluations
        ADD CONSTRAINT chk_evaluations_accuracy CHECK (accuracy_score BETWEEN 0 AND 40),
        ADD CONSTRAINT chk_evaluations_coverage CHECK (coverage_score BETWEEN 0 AND 40),
        ADD CONSTRAINT chk_evaluations_structural CHECK (structural_score BETWEEN 0 AND 20)
    """))
