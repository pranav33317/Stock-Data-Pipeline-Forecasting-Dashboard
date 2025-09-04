# Real-Time Stock Data Pipeline & Forecasting Dashboard

## Overview
End-to-end project that ingests stock data (API / scraping), stores it in a SQL database,
runs forecasting models (ARIMA / LSTM / Prophet), and serves an interactive Streamlit dashboard.

## Repo structure
- `data/` : raw & processed CSVs
- `notebooks/` : exploratory notebooks (optional)
- `src/` : main python modules
- `requirements.txt` : dependencies
- `Dockerfile` : container image
- `config.yaml` : API keys & DB config (fill before running)
- `run_pipeline.sh` : helper script for cron / automation

## Quick start (local)
1. Clone repo
2. Create and fill `config.yaml` (see `config.sample.yaml` for template)
3. Create virtualenv and install requirements:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the ETL once:
   ```bash
   python src/data_collection.py --once
   python src/forecasting.py --train
   ```
5. Launch the dashboard:
   ```bash
   streamlit run src/dashboard.py
   ```
