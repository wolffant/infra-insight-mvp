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
- **In-cluster (EKS)**: Uses the service account token automatically - recommended deployment target
- **Local dev**: K8s ingestion has networking limitations with minikube/Docker Desktop due to container isolation. For local testing, K8s ingestion can be skipped (will gracefully skip if unavailable)
- To enable locally (experimental): Ensure your `~/.kube/config` exists and mount it in docker-compose.yml worker volumes

## Run ingestion + detectors (ad-hoc)
```bash
docker compose exec worker python -m worker.cli ingest-jira
docker compose exec worker python -m worker.cli ingest-k8s
docker compose exec worker python -m worker.cli run-detectors
```

## Notes
- Jira API uses the v3 `/rest/api/3/search/jql` endpoint (migrated from deprecated `/rest/api/3/search`)
- Jira auth: email + API token (Atlassian Cloud)
- K8s ingestion gracefully skips if Kubernetes config unavailable (expected in local dev)
- Findings are **upserted** by (type, fingerprint)
- Next.js path aliases (`@/*`) configured in `tsconfig.json`
- API accessible from Next.js SSR via Docker service name (`http://api:8000`)
