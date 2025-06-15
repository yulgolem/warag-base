# Simple Makefile for container management

APP_TAG ?= writeragents

.PHONY: build up test down

build:
	docker build -t $(APP_TAG) .

up:
	docker compose up -d

test:
	docker compose run --rm app pytest

down:
	docker compose down
