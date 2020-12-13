# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:59:59 2020

@author: chond
"""

import datetime as dt
import yfinance as yf
import pandas as pd

# Getting a data for single stock ticker
# data = yf.download('TSLA', start='2020-11-01', end='2020-11-25', interval='5m')
# data = yf.download('TSLA', period='1mo', interval='5m')

# Getting data for multiple stocks
stocks = ['AMZN', 'MSFT', 'GOOG', 'TSLA', 'FB', 'BTC-USD']
start = dt.datetime.today() - dt.timedelta(3650)
end = dt.datetime.today()

prices = pd.DataFrame()
for stock in stocks:
    prices[stock] = yf.download(stock, start, end)['Adj Close']

# ohlcv = {}
# for stock in stocks:
#     ohlcv[stock] = yf.download(stock, start, end)

# Will handling NaN value in back-testing
prices.fillna(method='bfill', axis=0, inplace=True)

mean = prices.mean()
median = prices.median()
std = prices.std()

daily_return = prices.pct_change()
daily_return_shift = prices / prices.shift(1) - 1 # is the same as above

daily_return_mean = daily_return.mean()
daily_return_stf = daily_return.std()

# rolling mean
daily_return_sma = daily_return.rolling(window=20).mean() # simple moving average
daily_return_std = daily_return.rolling(window=20).std() # simple moving std
daily_return_ema = daily_return.ewm(span=20, min_periods=20).mean() # exponential moving average
daily_return_emstd = daily_return.ewm(span=20, min_periods=20).std() # exponential moving std

# visualization
prices.plot(subplots=True, layout=(3,2), title='Stock Prices', grid=True) # does not provide a lot of meaning
prices_z_scores = (prices - prices.mean()) / prices.std()
prices_z_scores.plot(title='Prices Z scores', grid=True)
