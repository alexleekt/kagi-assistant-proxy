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

```sh
python server.py
```

The proxy will be available at `http://localhost:$PORT`.