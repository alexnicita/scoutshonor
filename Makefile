SHELL := /bin/bash

.PHONY: help setup run test lint fmt migrate clean demo cron

help:
	@echo "Available targets:"
	@echo "  setup   - install deps / init env"
	@echo "  run     - run the primary app"
	@echo "  test    - run the test suite"
	@echo "  lint    - basic lint/sanity checks"
	@echo "  fmt     - format the codebase (noop if none)"
	@echo "  migrate - apply database migrations"
	@echo "  clean   - remove caches and build output"

setup:
	bash scripts/setup.sh

run:
	bash scripts/run.sh

test:
	bash scripts/test.sh

lint:
	bash scripts/lint.sh

fmt:
	bash scripts/fmt.sh

migrate:
	bash scripts/migrate.sh

cron:
	bash scripts/run_digest.sh

demo:
	bash scripts/demo-e2e.sh

clean:
	bash scripts/clean.sh
