#!/usr/bin/env bash
set -euo pipefail
source venv/bin/activate || true
python src/data_collection.py --once
python src/forecasting.py --train
echo "Pipeline run complete."
