# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 19:11:59 2020

@author: chond
"""

# import all dependencies
import datetime as dt
import yfinance as yf
from stocktrends import Renko # 3rd-party library renko implementation
 
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# time horizon set-up
start = dt.datetime.today() - dt.timedelta(365)
end = dt.datetime.today()

# getting data
stock = 'AAPL'
ohlcv = yf.download(stock, start, end)

# atr function to calculate brick size
def atr(df, n):
    df = df.copy()
    df['high-low'] = abs(df['High'] - df['Low'])
    df['high-pc'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['low-pc'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['true-range'] = df[['high-low', 'high-pc', 'low-pc']].max(axis=1, skipna=False)
    df['atr'] = df['true-range'].rolling(n).mean()
    df.dropna(inplace=True)
    return df

def renko(df_original):
    df = df_original.copy()
    df.reset_index(inplace=True) # convert index to column
    df = df.drop(['Close'], axis=1)
    df.columns  = ['date', 'open', 'high', 'low', 'close', 'volume'] # change column names
    renko_df = Renko(df)
    renko_df.brick_size = int(round(atr(df_original, 14)['atr'][-1], 0))
    return renko_df.get_ohlc_data()

df_renko = renko(ohlcv)

brick_size = 3
# df_renko['close-diff'] = df_renko['close'] - df_renko['close'].shift(1)
# df_renko.dropna(inplace=True)
# df_renko['bricks'] = df.loc[:, ('cdiff', )] / brick_size

