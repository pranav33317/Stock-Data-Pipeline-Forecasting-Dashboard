"""Data collection module.
Supports Alpha Vantage API and a scraping placeholder.
Writes raw CSV and inserts into SQL DB via database.py.
"""
import argparse, time, yaml, os, requests, pandas as pd
from datetime import datetime, timedelta
from database import Database

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def fetch_alpha_vantage(ticker, api_key, interval='1min', outputsize='compact'):
    # Simple Alpha Vantage TIME_SERIES_INTRADAY (note: free tier limits)
    base = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': ticker,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': api_key
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    # find the first key that contains Time Series
    ts_key = next((k for k in data.keys() if 'Time Series' in k), None)
    if ts_key is None:
        raise RuntimeError('Alpha Vantage response missing timeseries: ' + str(data))
    df = pd.DataFrame.from_dict(data[ts_key], orient='index')
    df = df.rename(columns=lambda c: c.split('. ')[1] if '. ' in c else c)
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df.columns = ['open','high','low','close','volume'][:len(df.columns)]
    df.index.name = 'timestamp'
    df['ticker'] = ticker
    return df.reset_index()

def main(once=False):
    cfg = load_config()
    db = Database(cfg['database'])
    tickers = cfg['pipeline']['tickers']
    key = cfg['api'].get('alpha_vantage_key')
    interval = str(cfg['pipeline'].get('interval_minutes',1)) + 'min'
    for t in tickers:
        try:
            df = fetch_alpha_vantage(t, key, interval=interval, outputsize='compact')
            # save raw
            raw_path = os.path.join(os.path.dirname(__file__), '..', 'data', f"{t.replace(':','_')}.csv")
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            df.to_csv(raw_path, index=False)
            # upsert into DB
            db.upsert_prices(df)
            print(f"Inserted {len(df)} rows for {t}")
        except Exception as e:
            print('Error fetching', t, e)
        if once:
            continue
        time.sleep(15)  # be polite on API rate limits

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    main(once=args.once)
