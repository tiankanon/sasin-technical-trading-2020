# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 14:43:21 2020

@author: chond
"""

# import all dependencies
import numpy as np
import pandas as pd
import copy
import yfinance as yf
import datetime as dt
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# atr function to detect breached price to initatiate a stop loss
def atr(df, n):
    df = df.copy()
    df['high-low'] = abs(df['High'] - df['Low'])
    df['high-pc'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['low-pc'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['true-range'] = df[['high-low', 'high-pc', 'low-pc']].max(axis=1, skipna=False)
    df['atr'] = df['true-range'].rolling(n).mean()
    df.dropna(inplace=True)
    return df['atr']

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

# basic data structure to implement back-testing
ohlcvs = copy.deepcopy(original_ohlcvs)
tickers_signal = {} # { 'MSFT': 'buy', 'AAPL': '', 'INTC': 'sell' }
tickers_signal_track = {}
tickers_return = {}

# calculate technical indicators
for ticker in tickers:
    print(f'Calculating ATR and rolling max price for {ticker}')
    ohlcvs[ticker]['atr'] = atr(ohlcvs[ticker], 20)
    ohlcvs[ticker]['rolling-max-price'] = ohlcvs[ticker]['High'].rolling(20).max()
    ohlcvs[ticker]['rolling-min-price'] = ohlcvs[ticker]['Low'].rolling(20).max()
    ohlcvs[ticker]['rolling-max-volume'] = ohlcvs[ticker]['Volume'].rolling(20).max()
    ohlcvs[ticker].dropna(inplace=True)
    tickers_signal[ticker] = ''
    tickers_signal_track[ticker] = []
    tickers_return[ticker] = []

# identifying signals and calculating return and incorporate the stop loss
for ticker in tickers:
    print(f'Calculating returns for {ticker}')
    for i in range(len(ohlcvs[ticker])):
        if (tickers_signal[ticker] == ''):
            tickers_return[ticker].append(0) # no signal equals no return for that candle        
            if (ohlcvs[ticker]['High'][i] >= ohlcvs[ticker]['rolling-max-price'][i] and 
                ohlcvs[ticker]['Volume'][i] > 1.5 * ohlcvs[ticker]['rolling-max-volume'][i-1]): # rule for break-out
                tickers_signal[ticker] = 'Buy' # initiate a buy signal
                tickers_signal_track[ticker].append('Start Buy')
            elif (ohlcvs[ticker]['Low'][i] <= ohlcvs[ticker]['rolling-min-price'][i] and 
                ohlcvs[ticker]['Volume'][i] > 1.5 * ohlcvs[ticker]['rolling-max-volume'][i-1]):
                tickers_signal[ticker] = 'Sell' # initiate a sell signal
                tickers_signal_track[ticker].append('Start Sell')
            else:
                tickers_signal_track[ticker].append('dnt')
                
        elif (tickers_signal[ticker] == 'Buy'):
            if (ohlcvs[ticker]['Low'][i] < ohlcvs[ticker]['Close'][i-1] - ohlcvs[ticker]['atr'][i-1]): # low price breached, stop loss
                tickers_signal[ticker] = '' # change from buy signal to nth to close off
                tickers_signal_track[ticker].append('Close Buy')
                tickers_return[ticker].append(((ohlcvs[ticker]['Close'][i-1] - ohlcvs[ticker]['atr'][i-1]) / ohlcvs[ticker]['Close'][i-1]) - 1)
            else:
                tickers_return[ticker].append((ohlcvs[ticker]['Close'][i] / ohlcvs[ticker]['Close'][i-1]) - 1)
                tickers_signal_track[ticker].append('Continue')
                
        elif (tickers_signal[ticker] == 'Sell'):
            if (ohlcvs[ticker]['High'][i] > ohlcvs[ticker]['Close'][i-1] + ohlcvs[ticker]['atr'][i-1]): # high price breached, stop loss
                tickers_signal[ticker] = '' # change from sell signal to nth to close off
                tickers_signal_track[ticker].append('Close Sell')
                tickers_return[ticker].append(((ohlcvs[ticker]['Close'][i-1] / (ohlcvs[ticker]['Close'][i-1] + ohlcvs[ticker]['atr'][i-1]))) - 1)
            else:
                tickers_return[ticker].append((ohlcvs[ticker]['Close'][i-1] / ohlcvs[ticker]['Close'][i]) - 1)
                tickers_signal_track[ticker].append('Continue')
    
    ohlcvs[ticker]['return'] = np.array(tickers_return[ticker])
    ohlcvs[ticker]['signal'] = np.array(tickers_signal_track[ticker])

# calculating overall strategy's KPIs
strategy = pd.DataFrame()
for ticker in tickers:
    strategy[ticker] = ohlcvs[ticker]['return']
strategy['return'] = strategy.mean(axis=1) # assume equal capital allocation
strategy['cumulative-return'] = (1 + strategy['return']).cumprod()
strategy_cagr = cagr(strategy)
strategy_volatility = volatility(strategy)
strategy_sharpe = sharpe(strategy, 0.01)
strategy_max_dd = maximum_drawdown(strategy)
strategy_calmar_ratio = calmar_ratio(strategy)

# KPIs for each stocks
individual_cagr = {}
individual_volatility = {}
individual_sharpe = {}
individual_max_dd = {}
individual_calmar_ratio = {}

for ticker in tickers:
    print(f'Calculating KPIs for {ticker}')
    individual_cagr[ticker] = cagr(ohlcvs[ticker])
    individual_volatility[ticker] = volatility(ohlcvs[ticker])
    individual_sharpe[ticker] = sharpe(ohlcvs[ticker], 0.01)
    individual_max_dd[ticker] = maximum_drawdown(ohlcvs[ticker])
    individual_calmar_ratio[ticker] = calmar_ratio(ohlcvs[ticker])

# create figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=strategy.index, y=strategy['cumulative-return'], name='Cumulative Return'))
# format figure
fig.update_layout(title_text=f'Cumulative Return of Portfolio of S1 - Maximum Drawdown Backtested {dt.datetime.today()}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Return')

plot(fig)