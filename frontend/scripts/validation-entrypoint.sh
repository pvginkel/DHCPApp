#!/usr/bin/env bash
set -euo pipefail

echo "=== Running backend tests ==="
cd /work/backend
poetry install --no-interaction
poetry run pytest -v --tb=short

echo "=== Running frontend tests ==="
cd /work/frontend
pnpm install --frozen-lockfile --config.confirmModulesPurge=false
pnpm build
pnpm playwright install chromium
pnpm playwright test --reporter=list
