.PHONY: up down logs bootstrap

up:
	cp -n .env.example .env || true
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

bootstrap:
	docker compose exec api alembic upgrade head
