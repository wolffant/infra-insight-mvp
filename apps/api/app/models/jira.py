from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Index
from sqlalchemy.sql import func
from app.models.base import Base

class JiraIssue(Base):
    __tablename__ = "jira_issues"
    key = Column(String, primary_key=True)
    issue_id = Column(String, nullable=False)
    project_key = Column(String, nullable=False)
    issue_type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    status_category = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    assignee = Column(String, nullable=True)
    reporter = Column(String, nullable=True)
    created_at_jira = Column(DateTime(timezone=True), nullable=True)
    updated_at_jira = Column(DateTime(timezone=True), nullable=True)
    raw = Column(JSON, nullable=False, default=dict)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_jira_issues_project", JiraIssue.project_key)
Index("ix_jira_issues_updated", JiraIssue.updated_at_jira)

class JiraChangelogEvent(Base):
    __tablename__ = "jira_changelog_events"
    id = Column(String, primary_key=True)
    issue_key = Column(String, nullable=False)
    history_id = Column(String, nullable=False)
    author = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    field = Column(String, nullable=True)
    from_string = Column(String, nullable=True)
    to_string = Column(String, nullable=True)
    raw = Column(JSON, nullable=False, default=dict)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_jira_changelog_issue", JiraChangelogEvent.issue_key)
Index("ix_jira_changelog_created", JiraChangelogEvent.created_at)
