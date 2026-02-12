# MCP Server MQL5

An **MCP Server** for MQL5 development, designed to integrate with Large Language Models (LLMs) like Claude. It provides intelligent access to the official [MQL5 documentation](https://www.mql5.com/en/docs), allowing generic AI models to become expert MQL5 coding assistants.

[![python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![checked-with-mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

## Features

- **📚 Smart Documentation Search**: Queries the official MQL5 search API to find the most relevant documentation pages.
- **🧠 Context-Aware Extraction**: Scrapes and cleans HTML content from MQL5.com, stripping unnecessary elements (scripts, styles, navs) to provide LLMs with pure, token-efficient context.
- **⚡ High Performance**: Implements intelligent caching to prevent redundant network requests and improve response times.
- **🛡️ Rate Limiting**: Built-in rate limiter ensures polite usage of MQL5.com resources, preventing IP bans.
- **🔄 Robust Networking**: Handles network errors gracefully with automatic user-agent rotation and retry logic.

## Installation

We recommend using [uv](https://github.com/astral-sh/uv) for dependency management, but standard `pip` is also supported.

### Using uv (Recommended)

To install efficiently with `uv`:

```bash
# Clone the repository
git clone https://github.com/jhontd03/mcp-server-mql5.git
cd mcp-server-mql5

# Install dependencies
uv sync
```

### Using pip

```bash
pip install .
```

## Configuration

### Claude Code (CLI)

To add this server to **Claude Code**, run the following command in your terminal (replacing `C:\path\to\mcp-server-mql5` with your actual absolute path):

```bash
claude mcp add mql5 -- uv --directory "C:\path\to\mcp-server-mql5" run mcp-server-mql5
```

> **Note**: On Windows, ensure you use the absolute path to the repository.

### Antigravity

To use this server with **Antigravity** or other MCP clients, add the following configuration to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "mql5": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/mcp-server-mql5",
        "run",
        "mcp-server-mql5"
      ]
    }
  }
}
```

*Note: Replace `C:/path/to/mcp-server-mql5` with the actual absolute path to your cloned repository.*

## Development

This project uses modern Python development tools to ensure code quality.

### Setup

```bash
# Install dependencies including dev tools
uv sync
```

### Quality Assurance

We enforce code quality using **Ruff** (linting/formatting) and **MyPy** (static type checking).

**Set up Pre-commit Hooks:**

This ensures checks run automatically before every commit.

```bash
uv run pre-commit install
```

**Run Checks Manually:**

```bash
# Run all pre-commit hooks on all files
uv run pre-commit run --all-files
```

### Testing

Run the test suite with `pytest`:

```bash
uv run pytest
```

## Components

- **`server.py`**: Main MCP server entry point.
- **`core/scraper.py`**: BeautifulSoup-based HTML extractor.
- **`core/search.py`**: Logic for parsing MQL5 search API results.
- **`core/web_client.py`**: Async HTTP client with `aiohttp`.
- **`core/utils.py`**: Rate limiters and logging utilities.

## License

Distributed under the MIT License. See `LICENSE` for more information.
