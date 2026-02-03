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

## Run ingestion + detectors (ad-hoc)
```bash
docker compose exec worker python -m worker.cli ingest-jira
docker compose exec worker python -m worker.cli ingest-k8s
docker compose exec worker python -m worker.cli run-detectors
```

## Notes
- Jira auth: email + API token (Atlassian Cloud).
- Kubernetes access: in-cluster service account on EKS, or local kubeconfig in dev.
- Findings are **upserted** by (type, fingerprint).
