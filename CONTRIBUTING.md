# Contributing

Thanks for your interest in contributing!

## How to contribute

1. Fork the repository and create your branch from `main`.
2. Create a virtual environment and install requirements.
3. Make your changes with clear, readable code and small commits.
4. Add or update documentation in `README.md` as needed.
5. Open a Pull Request with a clear title and description of the change.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m expense_tracker --help
```

## Code style

- Prefer explicit, descriptive names over abbreviations
- Keep functions small and focused
- Handle errors and edge cases gracefully
- Avoid external dependencies when standard library suffices

## Reporting issues

- Use GitHub Issues
- Provide steps to reproduce, expected vs actual behavior, and environment details
