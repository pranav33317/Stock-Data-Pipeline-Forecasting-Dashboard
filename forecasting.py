"""Forecasting module with ARIMA baseline and LSTM example.
"""
import argparse, os, yaml, pandas as pd, numpy as np
from database import Database
from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def train_arima(df, order=(5,1,0)):
    df = df.set_index('timestamp').sort_index()
    series = df['close'].astype(float)
    model = ARIMA(series, order=order)
    res = model.fit()
    forecast = res.forecast(steps=10)
    return forecast

def train_lstm(df, epochs=5):
    df = df.set_index('timestamp').sort_index()
    series = df['close'].astype(float).values.reshape(-1,1)
    scaler = MinMaxScaler()
    series_s = scaler.fit_transform(series)
    # create simple windows
    X, y = [], []
    seq_len = 10
    for i in range(len(series_s)-seq_len):
        X.append(series_s[i:i+seq_len])
        y.append(series_s[i+seq_len])
    X, y = np.array(X), np.array(y)
    model = Sequential([LSTM(32, input_shape=X.shape[1:]), Dense(1)])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=16, verbose=1)
    preds = model.predict(X[-1].reshape(1, X.shape[1], 1))
    preds = scaler.inverse_transform(preds)
    return preds.flatten()

def main(train=False):
    cfg = load_config()
    db = Database(cfg['database'])
    # simple: read from CSVs in data/
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    for f in os.listdir(data_dir):
        if not f.endswith('.csv'): continue
        df = pd.read_csv(os.path.join(data_dir,f), parse_dates=['timestamp'])
        print('Training for', f)
        arima_forecast = train_arima(df)
        lstm_pred = train_lstm(df, epochs=3)
        print('ARIMA:', arima_forecast)
        print('LSTM:', lstm_pred)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true')
    args = parser.parse_args()
    main(train=args.train)
