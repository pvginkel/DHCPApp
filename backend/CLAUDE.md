# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a DHCP monitoring application backend designed for homelab environments. It provides real-time visibility into DHCP lease information from dnsmasq services through a Flask REST API and Server-Sent Events (SSE) streaming.

## Development Commands

### Python Environment Setup
This project uses Poetry for dependency management:
```bash
poetry install        # Install dependencies
poetry shell          # Activate the virtual environment
```

### Running the Application
- **Development**: `poetry run python app.py` (runs with debug mode and reloader)
- **Production**: Set `FLASK_ENV=production` then run `poetry run python app.py`
- **Docker**: Use the provided scripts:
  - `./scripts/build.sh` - Build Docker image
  - `./scripts/run.sh` - Build and run container
  - `./scripts/stop.sh` - Stop running container

### Code Quality
Before committing, run all checks with a single command:
```bash
poetry run check   # Runs ruff, mypy, vulture, and pytest
```

Or run individual tools:
```bash
poetry run ruff check .                                           # Linting
poetry run mypy .                                                 # Type checking
poetry run vulture app/ vulture_whitelist.py --min-confidence 80  # Dead code detection
poetry run pytest                                                 # Full test suite
```

### Testing
- **Run all tests**: `poetry run pytest`
- **Run with coverage**: `poetry run pytest --cov=app`
- **Single test file**: `poetry run pytest test/test_dhcp_service.py`
- **Test API endpoints**: Use `curl -4` for IPv4-only requests (e.g., `curl -4 -s http://localhost:5001/api/v1/leases`)

### Configuration
- Main config via environment variables or config.py classes
- Key environment variables:
  - `DNSMASQ_CONFIG_FILE_PATH` - Path to main dnsmasq config (required)
  - `FLASK_ENV` - Environment (development/production/testing)
  - `HOST`, `PORT` - Server binding configuration
  - `UPDATE_MAC_VENDOR_DATABASE` - Enable/disable MAC vendor database updates (default: true for production, false for development/testing)

## Architecture Overview

### Core Design
- Flask application factory pattern with dependency injection
- Services stored in app context for cross-module access
- RESTful API design with `/api/v1/` prefix
- Server-Sent Events (SSE) for real-time updates
- OpenAPI documentation available at `/api/v1/openapi.json` endpoint

### Configuration Processing
The application implements dnsmasq's configuration parsing rules:
- Discovers config files via conf-dir directives
- Applies dnsmasq filtering (excludes backup files, hidden files, etc.)
- Parses dhcp-range and dhcp-host directives across all config files
- Cross-references lease data with static assignments

### File Structure
- `app.py` - Application entry point with development/production mode detection
- `config.py` - Configuration classes for different environments
- `app/` - Main application package with API, models, services, and utilities
- `data/` - Test data directory with sample dnsmasq configuration and lease files
- `scripts/` - Docker build/run scripts
- `test/` - Test suite using pytest

### Development Notes
- Uses Flask application factory pattern with dependency injection
- Services are stored in app context for cross-module access
- Comprehensive error handling with structured JSON responses
- Logging configured for development/production environments
- Docker setup includes volume mounts for dnsmasq data files

## Code Standards and Guidelines
- Tech stack: Python, Flask running on Kubernetes in production
- Use OOP design patterns
- Write Python type annotations for all functions and methods
- Use Python logging instead of print statements for debugging/info
- Track dependencies in `requirements.txt` without version pinning
- Keep .gitignore files brief and minimal
- Write only necessary code - avoid scaffolding or "future-useful" helper methods
- Don't start the Flask app automatically in development code

## Command Templates

The repository includes command templates for specific development workflows:

- When writing a product brief: @docs/commands/create_brief.md
- When planning a new feature: @docs/commands/plan_feature.md
- When doing code review: @docs/commands/code_review.md
- When planning or implementing a new feature, reference the product brief at @docs/product_brief.md

Use these files when the user asks you to perform the applicable action.
## Federated architecture model

We take part in a federated Architecture-as-Code model. The architecture for this repository is maintained in `docs/architecture/architecture.yaml`. Whenever a change is made in this repo that could impact an Enterprise Architecture / ArchiMate model modeling everything owned by this repo, nudge the user to spawn the `update-architecture` agent. The agent is incremental, so it's not a hard requirement that it runs on every change. Nudge a bit harder when significant changes are made (new managed host, new daemon, removed service, renamed external identity). When you are performing work unattended, feel free to invoke the agent yourself.

The tooling is installed on the operator's filesystem (not in this repo): the `/seed-architecture` skill (one-shot, authors the first artifact) and the `update-architecture` agent (permanent, incremental). Generated producers — those whose `docs/architecture/*.yaml` is a build output from a generator + annotation layer — use the `update-architecture-generated` agent instead, which edits the annotations and never the output. The producer manual at `~/.claude/architecture/producer-manual.md` is the authoritative vocabulary reference; the skill and agents read it from the operator's filesystem on startup.
