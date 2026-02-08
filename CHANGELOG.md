kagi-assistant-proxy/CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New model mappings for OpenAI-compatible API:
  - `openai/gpt-5-mini` → `gpt-5-mini`
  - `openai/gpt-oss-120b` → `gpt-oss-120b`
  - `moonshotai/kimi-k2.5` → `kimi-k2-5`
- Whitelist-based validation for Kagi SSE stream tags (`VALID_TAGS` in `lib/query/parse.py`)
- Support for `thread.html` tag parsing
- `.env.example` file with documentation for environment variables
- Comprehensive README.md with setup instructions
- Default model constant (`DEFAULT_MODEL`) for better maintainability
- AGPL-3.0 license headers added to all source files for license compliance

### Changed
- Updated HTTP headers to Firefox 137.0 on macOS for improved compatibility
- Improved error handling in SSE stream parser with clearer error messages
- Code formatting: standardized to double quotes throughout Python files
- Non-streaming response now correctly passes `prompt` and `kagi_model` to `stream_query()`

### Security
- Added `.env` and `mise.local.toml` to `.gitignore` to prevent secret leakage

## [0.1.0] - 2024-10-??

### Added
- Initial release of kagi-assistant-proxy
- OpenAI-compatible `/v1/chat/completions` endpoint with streaming support
- `/v1/models` endpoint for listing available models
- `/health` endpoint for health checks
- Kagi session management (`lib/auth.py`)
- SSE stream parsing for Kagi responses (`lib/query/parse.py`)
- Model mapping support:
  - `gpt-4` → `gpt-4o`
  - `gpt-4-turbo` → `gpt-4o`
  - `gpt-4o` → `gpt-4o`
  - `gpt-3.5-turbo` → `gpt-4o-mini`
  - `gpt-4o-mini` → `gpt-4o-mini`

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See [LICENSE](./LICENSE) for the full license text.

### Attribution

- Original author: [Cyberes](https://github.com/Cyberes)
- Contributors: Alex Lee