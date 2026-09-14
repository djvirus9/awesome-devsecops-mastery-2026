#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python_bin="${project_root}/.venv/bin/python"
[[ -x "$python_bin" ]] || { echo 'Run make setup first.' >&2; exit 2; }
exec "$python_bin" "$project_root/projects/k8s-gitops/validate_live.py" "$@"
