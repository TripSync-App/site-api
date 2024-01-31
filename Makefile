PHONY: stop remove build up

stop:
	docker stop site-api

remove:
	docker remove site-api

build:
	docker compose build --no-cache

up:
	docker compose up -d
