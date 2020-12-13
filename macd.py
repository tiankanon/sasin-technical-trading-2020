# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 12:00:23 2020

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
stock = 'AAPl'
ohlcv = yf.download(stock, start, end)

# macd function
def macd(df, fast_periods, slow_periods, signal_periods):
    df = df.copy()
    df['ma_fast'] = df['Adj Close'].ewm(span=fast_periods, min_periods=fast_periods).mean()
    df['ma_slow'] = df['Adj Close'].ewm(span=slow_periods, min_periods=slow_periods).mean()
    df['macd'] = df['ma_fast'] - df['ma_slow']
    df['signal'] = df['macd'].ewm(span=signal_periods, min_periods=signal_periods).mean()
    df['signal'].dropna(inplace=True)
    return df

# macd
df_macd = macd(ohlcv, 12, 26, 9)

# create figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['Adj Close'], name='price'))
fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['macd'], name='macd'), secondary_y=True)
fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['signal'], name='signal'), secondary_y=True)
fig.add_trace(go.Scatter(x=[df_macd.index[0], df_macd.index[-1]], y=[0, 0], name='reference'), secondary_y=True)

# format figure
fig.update_layout(title_text=f'MACD of {stock}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Price')
fig.update_yaxes(title_text='MACD & Signal', secondary_y=True)

# plot figure
plot(fig)