#!/usr/bin/env bash
# Parked, separately powered comma only. No controls or pandad are started.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD"
export JETLINK_BENCH=1
ln -sfn jetlink_repo/jetlink jetlink
exec /usr/local/venv/bin/python3 jetlink_repo/scripts/comma/jetlink_bench.py \
  --adapter openpilot.jetlink_adapter --modeld stock --start-owner \
  --model-sha256 87fe86ca0813c099efddf9173ba503be2e40ea4c5362c36812a44141f4cb07d4 \
  --model-name 'Chestnut Mountain Dew (stable 2026-11-09)' \
  --output "${OUTPUT:-/data/jetlink-bench/runs/$(date +%Y%m%d-%H%M%S)}" "$@"
