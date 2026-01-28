# Variables

help:
	@echo "Usage:"
	@echo "make [command]"
	@echo ""
	@echo "Commands:"
	@echo "	dev			Run the scrapers immediately for testing"
	@echo "	run			Run the scheduler and scrapers"
	@echo "	lint		Lint & correct errors"
	@echo "	build		Build docker image"
	@echo "	test		Run unit & integration tests"

# Targets
.PHONY: dev ruff test run build stop

dev:
	python main.py --once

lint:
	black .
	ruff check . --fix

build:
	$(DOCKER_COMPOSE) build

run:
	$(DOCKER_COMPOSE) up

stop:
	$(DOCKER_COMPOSE) down

test:
	pytest -v
