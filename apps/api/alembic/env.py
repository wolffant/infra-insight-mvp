from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.base import Base
# Import models to register metadata
from app.models.finding import Finding  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.jira import JiraIssue, JiraChangelogEvent  # noqa: F401
from app.models.k8s import K8sPodSnapshot, K8sEvent  # noqa: F401
from app.models.remediation_action import RemediationAction  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

def get_url():
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "infra_insight")
    user = os.getenv("POSTGRES_USER", "infra")
    pw = os.getenv("POSTGRES_PASSWORD", "infra")
    return f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    section = config.get_section(config.config_ini_section)
    section["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
