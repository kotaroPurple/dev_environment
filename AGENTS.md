# Repository Guidelines

## Project Structure & Module Organization
- `src/dev_environment/`: core library code. `data/` contains `BaseTimeSeries`, `BlockBuffer`, and helpers for sequential blocks. Future pipeline modules should live alongside.
- `docs/`: requirements, design notes, data-flow diagrams, and task tracker. Update these when architecture evolves.
- `todo/`: high-level intent from the product owner. Treat as upstream source when refining scope.
- Create `tests/` for unit and integration suites; mirror the package layout (e.g., `tests/data/test_models.py`).

## Build, Test, and Development Commands
- `uv sync`: create/update the virtual environment defined in `pyproject.toml`.
- `uv run python -m dev_environment.quickstart`: execute sample pipelines or smoke checks once implemented.
- `uv run ruff check src`: run linting; add `--fix` for safe auto-fixes.
- After adding tests, install `pytest` via `uv add --dev pytest` and run `uv run pytest`.

## Coding Style & Naming Conventions
- Python 3.12, 4-space indentation, 100-character line limit, two blank lines between top-level functions.
- Follow ruff rules `E`, `F`, `W`, `I`; imports are sorted with the bundled isort profile.
- Name modules with lowercase underscores, classes in PascalCase, functions in snake_case.
- Prefer dataclasses for immutable data containers and type hints for every public API.

## Testing Guidelines
- Write unit tests alongside each new module under `tests/` with `test_*.py` filenames.
- Aim for fast, deterministic tests that mock slow I/O; use fixtures for synthetic time-series blocks.
- For integration trails, build sample pipelines that validate block-by-block sequencing and error policies.
- Track coverage once the suite grows; target ≥80% relevant lines.

## Commit & Pull Request Guidelines
- Use concise, imperative messages with a scope prefix (`feat:`, `fix:`, `chore:`) as seen in history.
- Each commit should compile, lint, and (when present) pass tests.
- Pull requests must summarize intent, list impacted modules, link tasks/issues, and note manual test results or profiling data.
- Include updated docs or diagrams whenever behavior or architecture changes.
