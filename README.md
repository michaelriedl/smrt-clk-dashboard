# smrt-clk-dashboard
![Testing](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/pytest.yml/badge.svg)
![Linting](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/ruff.yml/badge.svg)
![Type Checking](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/ty.yml/badge.svg)

The dashboard implementation for the SMRT CLK hardware.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/macOS
# or
irm https://astral.sh/uv/install.ps1 | iex  # Windows

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run ty check .
```
