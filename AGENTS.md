# AGENTS.md

Guide for AI coding agents working in the kagi-assistant-proxy repository.

## Project Overview

A Python Flask proxy that exposes Kagi's LLM platform via an OpenAI-compatible API.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python server.py

# Run a single test (once pytest is configured)
pytest tests/test_specific.py::test_function_name -v

# Run all tests
pytest

# Format code (recommended: black, ruff)
black .
ruff check .

# Type check (recommended: mypy)
mypy lib/ server.py
```

**No test/lint tools currently configured.** Add to `requirements.txt` as needed.

## Code Style

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
2. **Group with blank lines between groups**
3. **Use absolute imports** for local modules

```python
# Standard library
import json
import os
from typing import Any, Optional

# Third-party
import requests
from flask import Flask, jsonify

# Local
from lib.auth import KagiSessionManager
from lib.headers import DEFAULT_HEADERS
```

### Naming Conventions

- **Functions/variables:** `snake_case` (e.g., `stream_query`)
- **Classes:** `PascalCase` (e.g., `KagiSessionManager`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_HEADERS`)
- **Private/internal:** `_leading_underscore` (e.g., `_logger`)

### String Formatting

- **Use double quotes** for all strings
- **Use f-strings** for formatting

```python
# Good
message = f"data: {json.dumps({'type': 'token'})}\n\n"

# Bad
message = 'data: %s\n\n' % json.dumps({'type': 'token'})
```

### Type Hints

**Use type hints** for all function signatures:

```python
from typing import Any, Dict, List, Optional

def get_models(session_key: str) -> List[Dict[str, str]]:
    ...

def get_session_key(self) -> Optional[str]:
    ...
```

### Error Handling

1. **Use try/except** for external operations (HTTP, I/O)
2. **Use logging**, not print statements
3. **Provide meaningful error messages**

```python
import logging

_logger = logging.getLogger("SERVER").getChild("STREAM")

try:
    response = requests.post(...)
    response.raise_for_status()
except Exception as e:
    _logger.error(f"Failed to delete thread {thread_id}: {e}")
```

### Documentation

**All public methods must have docstrings** using Google-style:

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

Define constants at module level:

```python
MODEL_MAPPING = {
    "openai/gpt-5-mini": "gpt-5-mini",
}

DEFAULT_HEADERS = {
    "accept": "application/json",
    ...
}
```

### Thread Safety

Use RLock for thread-safe operations:

```python
self._session_lock = threading.RLock()

with self._session_lock:
    return self._session_key
```

## Project Structure

```
.
├── server.py           # Flask entry point
├── lib/
│   ├── auth.py         # KagiSessionManager singleton
│   ├── headers.py      # DEFAULT_HEADERS
│   ├── mapping.py      # Model mapping utilities
│   ├── models.py       # Model fetching
│   └── query/
│       ├── query.py    # stream_query function
│       └── parse.py    # SSE stream parser
├── requirements.txt    # Dependencies
└── .env.example        # Environment template
```

## Environment

```bash
# Copy and edit environment file
cp .env.example .env
```

**Required:** `KAGI_SESSION_KEY` - From kagi.com cookies
**Optional:** `PORT` - Server port (default: 5000)

## Security

1. **Never commit secrets** - `.env` and `mise.local.toml` are in `.gitignore`
2. **Use environment variables** for configuration
3. **Session keys** managed via `KagiSessionManager` singleton

## License

AGPL-3.0 - All contributions must be compatible.
