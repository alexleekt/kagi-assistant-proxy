# kagi-assistant-proxy

_A proxy that exposes Kagi's LLM platform._

## Setup

### Environment Variables

Create a `.env` file in the project root:

```sh
cp .env.example .env
# Edit .env with your actual values
```

Or use `mise.local.toml`:

```sh
cp .env.example mise.local.toml
# Edit mise.local.toml with your actual values
```

Or set environment variables directly:

```sh
export KAGI_SESSION_KEY="your_session_key_here"
export PORT=5000  # optional, defaults to 5000
```

### Required Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `KAGI_SESSION_KEY` | Your Kagi session cookie | Log into kagi.com, open DevTools → Application → Cookies → `kagi_session` value |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Port to run the proxy server on |

## Running

### Local Development

```sh
python server.py
```

The proxy will be available at `http://localhost:$PORT`.

### Docker

#### Using Docker Compose (Recommended)

The easiest way to run the proxy with Docker:

```sh
docker-compose up
```

This will:
- Build the Docker image
- Start the container on the configured `PORT` (default: 5000)
- Automatically restart on failure

To run in the background:

```sh
docker-compose up -d
```

To stop the container:

```sh
docker-compose down
```

#### Using Docker Directly

Build the image:

```sh
docker build -t kagi-assistant-proxy .
```

Run the container:

```sh
docker run -p 5000:5000 \
  -e KAGI_SESSION_KEY="your_session_key_here" \
  kagi-assistant-proxy
```

Or specify a custom port:

```sh
docker run -p 8000:5000 \
  -e KAGI_SESSION_KEY="your_session_key_here" \
  kagi-assistant-proxy
```

### Docker Configuration

The Docker image is automatically built and published to GitHub Container Registry (GHCR) on every push to `master`/`main` and on version tags.

#### Pulling from GHCR

```sh
docker pull ghcr.io/ksmarty/kagi-assistant-proxy:latest
```

Or a specific version:

```sh
docker pull ghcr.io/ksmarty/kagi-assistant-proxy:v1.0.0
```

#### Environment Variables in Docker

All standard environment variables work with Docker. Set them using the `-e` flag or in a `.env` file with Docker Compose:

```sh
# With docker run
docker run -e KAGI_SESSION_KEY="your_key" kagi-assistant-proxy

# With docker-compose (set in .env file)
KAGI_SESSION_KEY="your_key"
PORT=5000
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

Copyright (C) 2024-2025  Cyberes, Alex Lee

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

See [LICENSE](./LICENSE) for the full license text.