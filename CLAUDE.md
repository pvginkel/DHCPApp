# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a DHCP monitoring application backend designed for homelab environments. It provides real-time visibility into DHCP lease information from dnsmasq services through a Flask REST API and Server-Sent Events (SSE) streaming.

## Development Commands

### Python Environment Setup
This project uses virtualenvwrapper. Activate the environment before running any Python commands:
```bash
workon dhcp-backend
```

### Running the Application
- **Development**: `python app.py` (runs with debug mode and reloader)
- **Production**: Set `FLASK_ENV=production` then run `python app.py`
- **Docker**: Use the provided scripts:
  - `./scripts/build.sh` - Build Docker image
  - `./scripts/run.sh` - Build and run container
  - `./scripts/stop.sh` - Stop running container

### Testing
- **Run all tests**: `pytest`
- **Run with coverage**: `pytest --cov=app`
- **Single test file**: `pytest test/test_dhcp_service.py`
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