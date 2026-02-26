# Variables
IMAGE_NAME = scraper-image
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
	uv run python -m src.main --once

lint:
	black .
	ruff check . --fix

build:
	docker build . -t $(IMAGE_NAME)

run:
	docker run $(IMAGE_NAME)

stop:
	docker stop -f $(IMAGE_NAME)
	docker rm -f $(IMAGE_NAME)

test:
	uv run pytest -v
