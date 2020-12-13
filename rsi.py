# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 15:32:59 2020

@author: chond
"""

# import all dependencies
import datetime as dt
import yfinance as yf
import numpy as np
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# time horizon set-up
start = dt.datetime.today() - dt.timedelta(365) # 1 year time-horizon
end = dt.datetime.today()

# getting data
stock = 'AAPL'
ohlcv = yf.download(stock, start, end)

# rsi function
def rsi(df, n):
    df = df.copy()
    df['delta-adj-close'] = df['Adj Close'] - df['Adj Close'].shift(1)
    df['gain'] = np.where(df['delta-adj-close'] >= 0, df['delta-adj-close'], 0)
    df['loss'] = np.where(df['delta-adj-close'] <= 0, abs(df['delta-adj-close']), 0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(( (n-1)*avg_gain[i-1] + gain[i] ) / n)
            avg_loss.append(( (n-1)*avg_loss[i-1] + loss[i] ) / n)
    df['avg_gain'] = np.array(avg_gain)
    df['avg_loss'] = np.array(avg_loss)
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    return df

# rsi
df_rsi = rsi(ohlcv, 14)

# create figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_rsi.index, y=df_rsi['Adj Close'], name='Price'))
fig.add_trace(go.Scatter(x=df_rsi.index, y=df_rsi['rsi'], name='rsi'), secondary_y=True)
fig.add_trace(go.Scatter(x=[df_rsi.index[0], df_rsi.index[-1]], y=[70,70], name='reference'), secondary_y=True)
fig.add_trace(go.Scatter(x=[df_rsi.index[0], df_rsi.index[-1]], y=[30,30], name='reference'), secondary_y=True)

# format figure
fig.update_layout(title_text=f'RSI of {stock}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Price')
fig.update_yaxes(title_text='RSI', secondary_y=True)

plot(fig)