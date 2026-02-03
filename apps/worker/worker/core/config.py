from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "infra_insight"
    POSTGRES_USER: str = "infra"
    POSTGRES_PASSWORD: str = "infra"

    JIRA_BASE_URL: str = ""
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_PROJECT_KEYS: str = ""
    JIRA_JQL_EXTRA: str = ""
    JIRA_MAX_ISSUES: int = 200

    K8S_MODE: str = "incluster"
    KUBECONFIG_PATH: str = "/root/.kube/config"
    K8S_NAMESPACE_FILTER: str = ""
    K8S_MAX_EVENTS: int = 500

    BACKLOG_AGING_DAYS: int = 30
    POD_RESTART_THRESHOLD: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
