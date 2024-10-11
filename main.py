import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from pprint import pprint

from notifications import send_email

# Defining functions

def trend_up(row):
    if row['fast'] > row['slow'] and row['Close'] > row['slow']:
        return 1
    else:
        return 0

def strong_trend(row):
    if row['trend_counter'] > 12:
        return 1
    else:
        return 0

# Initialize unauthenticated client

exchange = ccxt.binance({'options': {'defaultType': 'future'}})
exchange.load_markets()

# Search for all tickers trading on Binance, and add them to a list if the quote asset is USDT.

sym_list = []
symbols = exchange.fetch_tickers()
for ticker in symbols.items():

    # Added check to ensure market is actively traded

    if ticker[0].endswith(':USDT') and exchange.markets[ticker[0]]['active']:
        sym_list.append(ticker[1]['info']['symbol'])

all_prices = {}
counts = 0
export = ['Close', 'fast', 'slow', 'trend_counter']

# For all relevant assets trading on the target exchange, check if they have a candle history of at least 300, and check if they are above their trend.

for ticker in sym_list:
    df = pd.DataFrame(exchange.fetch_ohlcv(ticker, '4h', limit=300),
                      columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    if len(df) == 300:
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df.set_index('Time', inplace=True)

        df['fast'] = df.ta.ema(19)
        df['slow'] = df.ta.ema(31)

        df['trend_up'] = df.apply(trend_up, axis=1)
        # Create a new column with a counter
        df['counter'] = (df['trend_up'] != df['trend_up'].shift(1)).cumsum()
        # Group by the 'counter' column and calculate the cumulative count of 1 values
        df['trend_counter'] = df.groupby('counter')['trend_up'].cumsum()

        # Reset the count where value is 0

        df.loc[df['trend_up'] == 0, 'trend_counter'] = 0

        all_prices[ticker] = df[export]

        counts += 1
        print(f"{counts} items stored")
        print(ticker)
        time.sleep(1)

trending = {}
trended_hard = []
for ticker in all_prices.items():
    last_row = ticker[1].iloc[-1]
    if last_row['trend_counter'] > 20:
        trending[ticker[0]] = last_row['trend_counter']
    elif ticker[1]['trend_counter'].max() > 80:
        trended_hard.append(ticker[0])

sorted_trending_by_length = sorted(trending.items(), key=lambda x:x[1], reverse=True)
trending_dict = dict(sorted_trending_by_length)
print(trended_hard)

formatted_trending = '\n'.join([f'{int(tup[1])} {tup[0]}' for tup in sorted_trending_by_length])
formatted_trended = '\n'.join([*trended_hard])


send_email('Testing trend-finder', f'Currently trending:'
                                   f'\n{formatted_trending}'
                                   f'\nPreviously trended:'
                                   f'\n{trended_hard}')