#!/usr/bin/env bash
set -euo pipefail
LRD_PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LRD_PROJECT_DIR"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export MPLCONFIGDIR="$LRD_PROJECT_DIR/analysis/.cache/matplotlib"
export XDG_CACHE_HOME="$LRD_PROJECT_DIR/analysis/.cache"
LRD_PYTHON="$LRD_PROJECT_DIR/analysis/.venv/bin/python"
if [[ ! -x "$LRD_PYTHON" ]]; then
    echo "Create the project environment as described in analysis/README.md first." >&2
    exit 1
fi
"$LRD_PYTHON" -u analysis/measure.py > data/derived/measurement-run.log
"$LRD_PYTHON" -u analysis/shapes.py > data/derived/shape-run.log
"$LRD_PYTHON" analysis/figures.py
"$LRD_PYTHON" analysis/shape_figures.py
"$LRD_PYTHON" analysis/verify.py > data/derived/validation-run.log
echo "Tables, figures and numerical verification regenerated. Read CASE_STUDY.md and the limitations in research/observational-report.md."
