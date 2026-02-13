"""add remediation actions

Revision ID: 0002_add_remediation_actions
Revises: 0001_initial_schema
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_remediation_actions"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "remediation_actions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("finding_id", sa.String(), sa.ForeignKey("findings.id"), nullable=False),
        sa.Column("action_type", sa.String(), nullable=False),
        sa.Column("status", sa.Enum("proposed", "approved", "executing", "completed", "failed", "rejected", name="actionstatus"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("params", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("proposed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_remediation_actions_finding_id", "remediation_actions", ["finding_id"])
    op.create_index("ix_remediation_actions_status", "remediation_actions", ["status"])

def downgrade():
    op.drop_index("ix_remediation_actions_status", "remediation_actions")
    op.drop_index("ix_remediation_actions_finding_id", "remediation_actions")
    op.drop_table("remediation_actions")
    op.execute("DROP TYPE actionstatus")
