# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 21:34:54 2020

@author: chond
"""

# import all dependencies
import datetime as dt
import yfinance as yf
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# time horizon set-up
start = dt.datetime.today() - dt.timedelta(365) # 1 year time-horizon
end = dt.datetime.today()

# getting data
stock = 'AAPL'
ohlcv = yf.download(stock, start, end)

# atr function
def atr(df, n):
    df = df.copy()
    df['high-low'] = abs(df['High'] - df['Low'])
    df['high-pc'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['low-pc'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['true-range'] = df[['high-low', 'high-pc', 'low-pc']].max(axis=1, skipna=False)
    df['atr'] = df['true-range'].rolling(n).mean()
    df.dropna(inplace=True)
    return df
    
# bollinger bands function
def bollinger_bands(df, std, n):
    df = df.copy()
    df['ma'] = df['Adj Close'].rolling(n).mean()
    df['bb-up'] = df['ma'] + (std * df['ma'].rolling(n).std())
    df['bb-down'] = df['ma'] - (std * df['ma'].rolling(n).std())
    df['bb-range'] = df['bb-up'] - df['bb-down']
    df.dropna(inplace=True)
    return df

# atr and bb
df_atr_bb = atr(ohlcv, 14)
df_atr_bb = bollinger_bands(df_atr_bb, 2, 20)

# create figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_atr_bb.index, y=df_atr_bb['Adj Close'], name='price'))
fig.add_trace(go.Scatter(x=df_atr_bb.index, y=df_atr_bb['ma'], name='ma'))
fig.add_trace(go.Scatter(x=df_atr_bb.index, y=df_atr_bb['bb-up'], name='bb-up'))
fig.add_trace(go.Scatter(x=df_atr_bb.index, y=df_atr_bb['bb-down'], name='bb-down'))
fig.add_trace(go.Scatter(x=df_atr_bb.index, y=df_atr_bb['atr'], name='atr'), secondary_y=True)

# format figure
fig.update_layout(title_text=f'ATR & Bollinger Bands of {stock}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Price')
fig.update_yaxes(title_text='ATR', secondary_y=True)

plot(fig)