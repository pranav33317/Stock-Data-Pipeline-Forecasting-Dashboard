"""Streamlit dashboard showing price & forecasts.
Run with: streamlit run src/dashboard.py
"""
import streamlit as st, pandas as pd, os, glob
st.set_page_config(layout='wide')

st.title('Stock Forecasting Dashboard (Prototype)')
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
csvs = glob.glob(os.path.join(data_dir, '*.csv'))
if not csvs:
    st.warning('No data files found in data/. Run data_collection.py first.')
else:
    ticker = st.selectbox('Ticker', [os.path.basename(p).replace('.csv','') for p in csvs])
    df = pd.read_csv(os.path.join(data_dir, ticker + '.csv'), parse_dates=['timestamp'])
    st.write('Latest data sample:')
    st.dataframe(df.tail(10))
    st.line_chart(df.set_index('timestamp')['close'])
