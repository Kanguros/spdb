---
applyTo: "**"
---

# Project Overview

This repository provides a Python library and example for using SharePoint lists as a relational database, with Pydantic models and automatic relationship expansion.

## Coding Standards

- Use Black-compatible formatting (see Ruff config for line length and exclusions).
- All public functions and classes should have type annotations.
- Use snake_case for variable and function names.
- Use `Annotated` and `Field` for all Pydantic model attributes.
- Use `LookupField` for fields representing relationships (foreign keys).

## Development Workflow

- Use Poetry for dependency management.
- Run `pytest` before committing; all tests must pass.
- Use pre-commit hooks (Ruff, pytest, update_readme, etc.) before pushing.
- Document new modules and public APIs in the README.
- Do not hardcode credentials; use environment variables or config files for secrets.

## File Structure

- `spdb/`: Core library code (models, provider, base logic).
- `spdb_example/`: Example usage and models.
- `scripts/`: Utility scripts (e.g., README updater).
- `tests/`: Unit and integration tests, with mock data in `tests/data/`.

## Key Guidelines

- Write docstrings for all public functions and classes.
- Prefer context managers for resource handling.
- Avoid hardcoding sensitive data.
- Use mock data for tests; do not require live SharePoint access for CI.
- Keep each instruction and code change focused and atomic.
- Follow the structure and conventions in the provided example models and core classes.

## Tools and Dependencies

- Python 3.10+
- Poetry for dependency management
- Pydantic v2 for data models
- Office365-REST-Python-Client for SharePoint access
- Ruff for linting and formatting
- Pytest for testing
- Pre-commit for enforcing code quality

## Testing

- Place all tests in the `tests/` directory.
- Use pytest fixtures for reusable test setup.
- Use mock data in `tests/data/` for SharePoint-related tests.
- All new features must include corresponding tests.

## Miscellaneous

- Organize code with clear separation between core logic, examples, scripts, and tests.
- Keep instructions and documentation up to date as the project evolves.
- Store this file in version control and update as standards change.
