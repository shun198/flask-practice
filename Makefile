RUN_APP=docker compose exec app poetry run flask --app main

prepare:
	docker compose up -d --build

up:
	docker compose up -d

build:
	docker compose build

down:
	docker compose down

routes:
	${RUN_APP} routes

shell:
	${RUN_APP} shell

format:
	docker compose exec app poetry run black .
	docker compose exec app poetry run isort .
