# Makefile for AI Tech Exec Recruiter

PY ?= python3
PIP ?= pip3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: setup run test lint fmt clean

setup:
	$(PY) -m venv $(VENV)
	$(ACTIVATE) && pip install -U pip
	$(ACTIVATE) && pip install -r requirements.txt

run:
	$(ACTIVATE) && uvicorn src.app:app --reload --port $${PORT:-8000}

test:
	PYTHONPATH=. $(ACTIVATE) && pytest -q

lint:
	$(ACTIVATE) && ruff check src tests $(FIX)

fmt:
	$(ACTIVATE) && black src tests scripts

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache **/__pycache__ */**/__pycache__
