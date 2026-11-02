#!/usr/bin/env bash
# Frontend e backend locais na mesma porta; nunca executar com fixtures de QA.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
if [[ ! -f .env ]]; then
  echo "Crie .env a partir de .env.example e configure XANO_API_BASE_URL." >&2
  exit 1
fi
set -a
source .env
set +a
if [[ -z "${XANO_API_BASE_URL:-}" ]]; then
  echo "Configure XANO_API_BASE_URL no .env antes de iniciar." >&2
  exit 1
fi
.venv/bin/reflex run --env prod --single-port --backend-port "${VET_TECH_PORT:-3000}" 2>&1 | tee reflex.log
