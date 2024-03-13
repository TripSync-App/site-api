PHONY: stop remove build build-force up

stop:
	docker stop site-api

remove:
	docker remove site-api

build:
	docker compose build 

build-force:
	docker compose build --no-cache

up:
	docker compose up -d
