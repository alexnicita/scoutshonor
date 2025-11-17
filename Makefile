# Simple, language-lean Makefile with script wrappers

.PHONY: help setup run test lint fmt

help:
	@echo "Available targets:"
	@echo "  make setup  - install deps / init env"
	@echo "  make run    - run the primary app"
	@echo "  make test   - run the test suite"
	@echo "  make lint   - basic lint/sanity checks"
	@echo "  make fmt    - format the codebase (noop if none)"

setup:
	bash scripts/setup-env.sh

run:
	bash scripts/run-server.sh

test:
	bash scripts/run-tests.sh

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src tests; \
	else \
		echo "ruff not found; running basic syntax check"; \
		python3 -m py_compile $(find src -name "*.py"); \
	fi

fmt:
	bash scripts/format.sh

.PHONY: cron
cron:
	bash scripts/run_digest.sh

.PHONY: demo
demo:
	bash scripts/demo-e2e.sh
