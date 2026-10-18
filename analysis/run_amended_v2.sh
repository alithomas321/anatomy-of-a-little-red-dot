#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
mkdir -p data/derived/amended-v2 figures/amended-v2
analysis/.venv/bin/python analysis/amended_v2_extraction.py > data/derived/amended-v2/extraction-run.log
analysis/.venv/bin/python analysis/amended_v2_lines.py > data/derived/amended-v2/line-run.log
analysis/.venv/bin/python analysis/amended_v2_figures.py
analysis/.venv/bin/python analysis/verify_amended_v2.py | tee data/derived/amended-v2/verification-run.log
