# AGENTS.md

Guide for AI coding agents working in the kagi-assistant-proxy repository.

## Project Overview

A Python Flask proxy that exposes Kagi's LLM platform via an OpenAI-compatible API.

## Build / Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python server.py

# Server will start on port 5000 (or PORT env var)
```

## Test Commands

**No test framework is currently configured.** To add tests:

```bash
# Install pytest (add to requirements.txt)
pip install pytest

# Run all tests (once configured)
pytest

# Run a single test
pytest tests/test_specific.py::test_function_name -v

# Run with coverage
pytest --cov=lib --cov-report=term-missing
```

## Lint/Format Commands

**No linting/formatting tools configured.** Recommended setup:

```bash
# Install tools (add to requirements.txt or requirements-dev.txt)
pip install black ruff mypy

# Format code with black
black .

# Lint with ruff (faster alternative to flake8)
ruff check .

# Type check with mypy
mypy lib/ server.py
```

## Code Style Guidelines

### License Headers
**ALL Python files must include the AGPL-3.0 license header:**

```python
# kagi-assistant-proxy - A proxy that exposes Kagi's LLM platform
# Copyright (C) 2024-2025  Cyberes, Alex Lee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

### Imports

1. **Order:** Standard library → Third-party → Local modules
2. **Group imports with blank lines between groups**
3. **Use absolute imports** for local modules (e.g., `from lib.auth import ...`)

```python
# Standard library
import json
import os
from datetime import datetime
from typing import Any, Optional

# Third-party
import requests
from flask import Flask, jsonify

# Local
from lib.auth import KagiSessionManager
from lib.headers import DEFAULT_HEADERS
```

### Naming Conventions

- **Functions/variables:** `snake_case` (e.g., `stream_query`, `kagi_session_key`)
- **Classes:** `PascalCase` (e.g., `KagiSessionManager`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_HEADERS`, `MODEL_MAPPING`)
- **Private/internal:** `_leading_underscore` (e.g., `_logger`, `_kagi_session_manager`)

### String Formatting

- **Use double quotes** for all strings (project convention)
- **Use f-strings** for string formatting (Python 3.6+)

```python
# Good
message = f"data: {json.dumps({'type': 'token'})}\n\n"

# Bad
message = 'data: %s\n\n' % json.dumps({'type': 'token'})
```

### Type Hints

**Use type hints** for all function signatures and important variables:

```python
from typing import Any, Dict, List, Optional

def get_models(session_key: str) -> List[Dict[str, str]]:
    ...

def get_session_key(self) -> Optional[str]:
    ...
```

### Error Handling

1. **Use try/except blocks** for external operations (HTTP requests, file I/O)
2. **Use logging** for errors, not print statements (see `lib/query/query.py`)
3. **Provide meaningful error messages** with context

```python
import logging

_logger = logging.getLogger("SERVER").getChild("STREAM")

try:
    response = requests.post(...)
    response.raise_for_status()
except Exception as e:
    _logger.error(f"Failed to delete thread {thread_id}: {e}")
    # Don't re-raise if it's acceptable to continue
```

### Documentation

1. **All public methods must have docstrings**
2. Use Google-style docstrings (existing pattern)
3. Include Args, Returns, and Raises sections when applicable

```python
def set_session_key(self, key: str) -> None:
    """
    Set the session key.
    Thread-safe setter for session key.

    Args:
        key (str): The new session key
    """
    ...
```

### Constants

Define constants at module level, not inside functions:

```python
# At top of file
MODEL_MAPPING = {
    "openai/gpt-5-mini": "gpt-5-mini",
    "openai/gpt-oss-120b": "gpt-oss-120b",
}

DEFAULT_HEADERS = {
    "accept": "application/json",
    ...
}
```

### Security

1. **Never commit secrets** - `.env` and `mise.local.toml` are in `.gitignore`
2. **Use environment variables** for configuration
3. **Session keys** are managed via `KagiSessionManager` singleton

### Thread Safety

The project uses threading for session management:

```python
# Use RLock for reentrant thread-safe operations
self._session_lock = threading.RLock()

# Always acquire lock when accessing shared state
with self._session_lock:
    return self._session_key
```

## Project Structure

```
.
├── server.py           # Flask application entry point
├── lib/
│   ├── __init__.py
│   ├── auth.py         # KagiSessionManager (singleton)
│   ├── headers.py      # DEFAULT_HEADERS constant
│   ├── models.py       # Model fetching utilities
│   └── query/
│       ├── __init__.py
│       ├── query.py    # stream_query() function
│       └── parse.py    # SSE stream parser
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # Documentation
```

## Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Kagi session key
# Or use mise.local.toml for mise users
```

**Required:** `KAGI_SESSION_KEY` - Get from kagi.com cookies (kagi_session)
**Optional:** `PORT` - Server port (default: 5000)

## Dependencies

See `requirements.txt`:
- `requests==2.32.3` - HTTP client
- `flask==3.1.1` - Web framework

## License

AGPL-3.0 - All contributions must be compatible.
