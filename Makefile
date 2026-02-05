.PHONY: up down logs bootstrap up-with-k8s down-all

up:
	cp -n .env.example .env || true
	docker compose up --build

up-with-k8s:
	@echo "Starting minikube..."
	@minikube status >/dev/null 2>&1 || minikube start
	@echo "Starting docker compose services..."
	cp -n .env.example .env || true
	docker compose up --build

down:
	docker compose down -v

down-all:
	docker compose down -v
	minikube stop

logs:
	docker compose logs -f --tail=200

bootstrap:
	docker compose exec api alembic upgrade head
