# Contributing

**How to contribute to SPDB.**

## Guidelines

- Open issues or submit pull requests for improvements
- Run `pytest` before committing; all tests must pass
- Use pre-commit hooks (Ruff, pytest, update_readme, etc.) before pushing
- Document new modules and public APIs in the README
- Do not hardcode credentials; use environment variables or config files

## Development Workflow

1. Fork the repository
2. Clone your fork
3. Create a new branch for your change
4. Make changes and add tests
5. Run tests and pre-commit hooks
6. Submit a pull request

## Code Standards

- Use Black-compatible formatting
- All public functions/classes must have type annotations
- Use snake_case for names
- Use `Annotated` and `Field` for Pydantic model attributes
- Use `LookupField` for relationships
- Write docstrings for all public functions/classes
