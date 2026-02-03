"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "services",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("selectors", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "findings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("remediation", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("type", "fingerprint", name="uq_findings_type_fingerprint"),
    )

    op.create_table(
        "jira_issues",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("issue_id", sa.String(), nullable=False),
        sa.Column("project_key", sa.String(), nullable=False),
        sa.Column("issue_type", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("status_category", sa.String(), nullable=True),
        sa.Column("priority", sa.String(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("assignee", sa.String(), nullable=True),
        sa.Column("reporter", sa.String(), nullable=True),
        sa.Column("created_at_jira", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at_jira", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_jira_issues_project", "jira_issues", ["project_key"])
    op.create_index("ix_jira_issues_updated", "jira_issues", ["updated_at_jira"])

    op.create_table(
        "jira_changelog_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("issue_key", sa.String(), nullable=False),
        sa.Column("history_id", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("field", sa.String(), nullable=True),
        sa.Column("from_string", sa.String(), nullable=True),
        sa.Column("to_string", sa.String(), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_jira_changelog_issue", "jira_changelog_events", ["issue_key"])
    op.create_index("ix_jira_changelog_created", "jira_changelog_events", ["created_at"])

    op.create_table(
        "k8s_pod_snapshots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cluster", sa.String(), nullable=True),
        sa.Column("namespace", sa.String(), nullable=False),
        sa.Column("pod", sa.String(), nullable=False),
        sa.Column("node", sa.String(), nullable=True),
        sa.Column("phase", sa.String(), nullable=True),
        sa.Column("restart_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("raw", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.create_index("ix_k8s_pod_ns_pod", "k8s_pod_snapshots", ["namespace", "pod"])

    op.create_table(
        "k8s_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("cluster", sa.String(), nullable=True),
        sa.Column("namespace", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("involved_kind", sa.String(), nullable=True),
        sa.Column("involved_name", sa.String(), nullable=True),
        sa.Column("first_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_k8s_events_ns_type", "k8s_events", ["namespace", "type"])

def downgrade():
    op.drop_index("ix_k8s_events_ns_type", table_name="k8s_events")
    op.drop_table("k8s_events")
    op.drop_index("ix_k8s_pod_ns_pod", table_name="k8s_pod_snapshots")
    op.drop_table("k8s_pod_snapshots")
    op.drop_index("ix_jira_changelog_created", table_name="jira_changelog_events")
    op.drop_index("ix_jira_changelog_issue", table_name="jira_changelog_events")
    op.drop_table("jira_changelog_events")
    op.drop_index("ix_jira_issues_updated", table_name="jira_issues")
    op.drop_index("ix_jira_issues_project", table_name="jira_issues")
    op.drop_table("jira_issues")
    op.drop_table("findings")
    op.drop_table("services")
