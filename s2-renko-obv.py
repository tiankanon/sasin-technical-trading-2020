# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 23:32:17 2020

@author: chond
"""

import numpy as np
import pandas as pd
import copy
import time
import yfinance as yf
import datetime as dt
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm # linear regression
from stocktrends import Renko # 3rd-party library renko implementation

# atr function
def atr(df, n):
    df = df.copy()
    df['high-low'] = abs(df['High'] - df['Low'])
    df['high-pc'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['low-pc'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['true-range'] = df[['high-low', 'high-pc', 'low-pc']].max(axis=1, skipna=False)
    df['atr'] = df['true-range'].rolling(n).mean()
    df.dropna(inplace=True)
    return df['atr']

# ordinary least square method => linear regression
def slope(ser, n):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

# renko
def renko(df_original):
    df = df_original.copy()
    df.reset_index(inplace=True) # convert index to column
    df.drop(['Close'], axis=1)
    df.columns  = ['date', 'open', 'high', 'low', 'close', 'volume'] # change column names
    renko_df = Renko(df)
    renko_df.brick_size = int(round(atr(df_original, 14)['atr'][-1], 0))
    return renko_df.get_ohlc_data()

# obv function
def obv(df):
    df = df.copy()
    df['daily-return'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily-return'] > 0, 1, -1)
    df['direction'][0] = 0
    df['volume-direction'] = df['Volume'] * df['direction']
    df['obv'] = df['volume-direction'].cumsum()
    return df

# kpis
def cagr(df):
    df = df.copy()
    df['cumulative-return'] = (1 + df['return']).cumprod()
    n = len(df) / (252) # number of trading days per 1 year
    cagr = (df['cumulative-return'].tolist()[-1])**(1/n) - 1
    return cagr

def volatility(df):
    df = df.copy()
    annual_volatility = df['return'].std() * np.sqrt(252)
    return annual_volatility

def sharpe(df, rf):
    df = df.copy()
    sr = (cagr(df) - rf) / volatility(df)
    return sr

def maximum_drawdown(df):
    df = df.copy()
    df['cumulative-return'] = (1 + df['return']).cumprod() # value today
    df['cumulative-rolling-max'] = df['cumulative-return'].cummax()
    df['drawdown'] = df['cumulative-rolling-max'] - df['cumulative-return']
    df['drawdown-percent'] = df['drawdown'] / df['cumulative-rolling-max']
    m_dd = df['drawdown-percent'].max()
    return m_dd

def calmar_ratio(df):
    df = df.copy()
    c_r = cagr(df) / maximum_drawdown(df)
    return c_r

# time horizon set-up
start = dt.datetime.today() - dt.timedelta(365)
end = dt.datetime.today()

# NASDAQ most active by dollars stocks
original_tickers = ['TSLA', 'AAPL', 'AMZN', 'MSFT', 'QCOM', 'FB', 'AMD', 'NVDA', 'NFLX', 'ADBE']
original_ohlcvs = {}

# downloading data for all tickers
for ticker in original_tickers:
    original_ohlcvs[ticker] = yf.download(ticker, start, end, interval='1d')

# assigning new tickers
tickers = original_ohlcvs.keys()