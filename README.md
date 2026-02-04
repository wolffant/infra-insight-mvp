# Infra Insight MVP

An MVP "delivery + reliability intelligence" platform for **AWS + EKS** that ingests:
- Jira issues + changelog history
- Kubernetes events + pod restart data

It produces **evidence-backed findings** (detectors) and shows them in a simple UI with trends.

## Local dev quickstart
```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000/docs
- Web: http://localhost:3000

## Bootstrap DB
```bash
docker compose exec api alembic upgrade head
```

## Configuration

### Jira Setup
1. Update `.env` with your Atlassian Cloud credentials:
   - `JIRA_BASE_URL`: Your Jira domain (e.g., `https://mycompany.atlassian.net`)
   - `JIRA_EMAIL`: Your Atlassian email
   - `JIRA_API_TOKEN`: API token from [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - `JIRA_PROJECT_KEYS`: Comma-separated project keys to ingest (e.g., `PROJ1,PROJ2`)

### Kubernetes Setup
- **In-cluster (EKS)**: Uses the service account token automatically
- **Local dev**: Ensure your `~/.kube/config` is valid (or update `KUBECONFIG_PATH` in `.env`)

## Run ingestion + detectors (ad-hoc)
```bash
docker compose exec worker python -m worker.cli ingest-jira
docker compose exec worker python -m worker.cli ingest-k8s
docker compose exec worker python -m worker.cli run-detectors
```

## Notes
- Jira API now uses the v3 search/jql endpoint (migrated from deprecated `/rest/api/3/search`)
- Jira auth: email + API token (Atlassian Cloud)
- Kubernetes access: in-cluster service account on EKS, or local kubeconfig in dev
- Findings are **upserted** by (type, fingerprint)
- Next.js requires `tsconfig.json` with path aliases configured for `@/*` imports
