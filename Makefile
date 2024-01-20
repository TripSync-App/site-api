PHONY: stop remove build up

stop:
	docker stop site_api

remove:
	docker remove site_api

build:
	docker compose build --no-cache

up:
	docker compose up -d
