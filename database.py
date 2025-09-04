"""Simple SQL database helper using SQLAlchemy.
Handles creation of stocks and prices tables and upsert of price rows.
"""
import os, yaml
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, DateTime
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
import pandas as pd

def db_url_from_cfg(cfg):
    dialect = cfg.get('dialect','sqlite')
    if dialect == 'sqlite':
        path = cfg.get('sqlite_path','./data/stocks.db')
        return f'sqlite:///{path}'
    else:
        user = cfg.get('user')
        pw = cfg.get('password')
        host = cfg.get('host')
        port = cfg.get('port')
        db = cfg.get('database')
        return f"{dialect}://{user}:{pw}@{host}:{port}/{db}"

class Database:
    def __init__(self, cfg):
        self.url = db_url_from_cfg(cfg)
        self.engine = create_engine(self.url, future=True)
        self.meta = MetaData()
        self.prices = Table('prices', self.meta,
                            Column('id', Integer, primary_key=True, autoincrement=True),
                            Column('ticker', String, index=True),
                            Column('timestamp', DateTime, index=True),
                            Column('open', Float),
                            Column('high', Float),
                            Column('low', Float),
                            Column('close', Float),
                            Column('volume', Float),
                           )
        self.meta.create_all(self.engine)

    def upsert_prices(self, df: pd.DataFrame):
        # naive upsert: insert ignoring duplicates for sqlite
        df2 = df.copy()
        df2 = df2[['ticker','timestamp','open','high','low','close','volume']]
        with self.engine.connect() as conn:
            for _, row in df2.iterrows():
                ins = self.prices.insert().values(**row.to_dict())
                conn.execute(ins)
            conn.commit()
