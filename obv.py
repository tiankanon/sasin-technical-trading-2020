# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 22:07:43 2020

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

# obv function
def obv(df):
    df = df.copy()
    df['daily-return'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily-return'] > 0, 1, -1)
    df['direction'][0] = 0
    df['volume-direction'] = df['Volume'] * df['direction']
    df['obv'] = df['volume-direction'].cumsum()
    return df

# obv
df_obv = obv(ohlcv)

# create figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df_obv.index, y=df_obv['Adj Close'], name='price'))
fig.add_trace(go.Scatter(x=df_obv.index, y=df_obv['obv'], name='obv'), secondary_y=True)

# format figure
fig.update_layout(title_text=f'OBV of {stock}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Price')
fig.update_yaxes(title_text='OBV', secondary_y=True)

plot(fig)