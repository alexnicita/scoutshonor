# Repository Guidelines

## Project Structure & Module Organization
- Root layout is currently minimal. Use a language‑agnostic structure as you add code:
  - `src/`: production code grouped by module or feature
  - `tests/`: test files mirroring `src/` layout
  - `scripts/`: one‑off or dev utility scripts
  - `docs/` and `assets/`: documentation and static files
  - `examples/`: runnable examples and snippets
- Keep modules small and cohesive. Prefer one clear responsibility per file.

## Build, Test, and Development Commands
- This repository has no build tooling yet. Prefer Make targets so commands stay uniform across environments:
  - `make setup`: install dependencies, initialize env
  - `make run`: run the primary app or example
  - `make test`: run the full test suite
  - `make lint` / `make fmt`: lint and format the codebase
- If Make is unavailable, provide equivalent `scripts/` wrappers (e.g., `scripts/test.sh`).

## Coding Style & Naming Conventions
- Indentation: 2 spaces for config/markup; 4 spaces for source code.
- Filenames: `kebab-case` for scripts in `scripts/`, `snake_case` for code in `src/` and tests in `tests/`.
- Keep functions short and pure where possible; avoid hidden side effects.
- Add a brief module header explaining purpose and key dependencies.

## Testing Guidelines
- Place tests in `tests/` with names `test_<module>.ext` or `<module>_test.ext`.
- Aim for ≥80% coverage once a test harness is in place.
- Prefer fast, deterministic unit tests; use fixtures for I/O and network boundaries.
- Example: `make test` should run all tests and print a summary.

## Commit & Pull Request Guidelines
- Use Conventional Commits where practical (e.g., `feat: add parser`, `fix: handle empty input`).
- Keep commits focused and atomic; include rationale in the body when non‑obvious.
- Pull Requests: include a clear description, linked issues (`Closes #123`), and screenshots or logs when behavior changes.
- Request review early for architectural choices; mark as draft if incomplete.

## Security & Configuration Tips
- Never commit secrets. Use `.env` locally and provide `.env.example` with non‑sensitive defaults.
- Pin dependencies where supported; document minimum versions in `README.md` or `Makefile` comments.

