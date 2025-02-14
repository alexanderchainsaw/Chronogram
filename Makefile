PROJECT_FOLDER = chronogram

up:
	docker compose -f docker-compose.yml up -d
down:
	docker compose -f docker-compose.yml down
build:
	docker compose build
test:
	poetry run pytest
lint:
	poetry run black ${PROJECT_FOLDER}
	poetry run ruff check ${PROJECT_FOLDER}
run: down test lint build up