# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 22:44:55 2020

@author: chond
"""

# import all dependencies
import datetime as dt
import yfinance as yf
import numpy as np

# time horizon set-up
start = dt.datetime.today() - dt.timedelta(365) # 1 year time-horizon
end = dt.datetime.today()

# getting data
stock = 'AAPL'
ohlcv = yf.download(stock, start, end)

# cagr function
def cagr(df):
    df = df.copy()
    df['daily-return'] = df['Adj Close'].pct_change()
    df['cumulative-return'] = (1 + df['daily-return']).cumprod()
    n = len(df) / 252 # number of trading days per year
    cagr = (df['cumulative-return'][-1])**(1/n) - 1
    return cagr

# volatility function
def volatility(df):
    df = df.copy()
    df['daily-return'] = df['Adj Close'].pct_change()
    annual_volatility = df['daily-return'].std() * np.sqrt(252)
    return annual_volatility

# sharpe function
def sharpe(df, rf):
    df = df.copy()
    sr = (cagr(df) - rf) / volatility(df)
    return sr

# maximum drawdown function
def maximum_drawdown(df):
    df = df.copy()
    df['daily-return'] = df['Adj Close'].pct_change()
    df['cumulative-return'] = (1 + df['daily-return']).cumprod() # value today
    df['cumulative-rolling-max'] = df['cumulative-return'].cummax()
    df['drawdown'] = df['cumulative-rolling-max'] - df['cumulative-return']
    df['drawdown-percent'] = df['drawdown'] / df['cumulative-rolling-max']
    m_dd = df['drawdown-percent'].max()
    return m_dd

# calmar ratio function
def calmar_ratio(df):
    df = df.copy()
    c_r = cagr(df) / maximum_drawdown(df)
    return c_r

# kpis
ca = cagr(ohlcv)
vol = volatility(ohlcv)
sr = sharpe(ohlcv, 0.015)
mdd = maximum_drawdown(ohlcv)
calmar_ratio(ohlcv)


    