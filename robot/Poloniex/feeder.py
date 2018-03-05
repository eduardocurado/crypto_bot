import time
from datetime import datetime, timedelta

import numpy as np
from poloniex import Poloniex

from robot.Decision import features
from robot.Extractor import tickers


def get_historical_data(coin, start):
    polo = Poloniex()
    print('Fetching External Data')
    # historical = polo.returnChartData(coin, 300)
    historical = polo.returnChartData(coin, 300, start=start)
    print('Got External Data')
    inserted = 0
    for h in historical:
        # tick = np.mean((float(h['close']) + float(h['open']) + float(h['low']) + float(h['high'])))
        tick = float(h['close'])
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(h['date']))
        try:
            tickers.insert_tickers(date, coin, tick, 0)
        except Exception:
            continue
        features.update_indicators(date, coin, 0)
        inserted += 1
    return inserted


def get_tick(coin):
    polo = Poloniex()
    intermediate_data = polo('returnTicker')[coin]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last = intermediate_data['last']
    tickers.insert_tickers(date, coin, last, 0)
    return last, date


def get_tick_interval(coin, last_date, interval):
    polo = Poloniex()
    h = polo.returnChartData(coin, interval, start=last_date)
    tick = np.mean((float(h['close']) + float(h['open']) + float(h['low']) + float(h['high'])))
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(h['date']))
    try:
        tickers.insert_tickers(date, coin, tick, 0)
    except Exception:
        print("Error Inserting Tick")
        return None
    return h


# NUMBER OF TICKERS IN A SCREEN TICKER
# interval = H
# Ticker interval = 300s = 5 m
# H*5m = 60H/5M = 12


def get_historical_screen(interval, coin, screen):
    x = 0
    tickers_df = tickers.get_all_tickers_screen(coin, 0)
    for index, row in tickers_df.iterrows():
        x += 1
        if not (x % (interval*12)):
            start = x-interval*12
            end = x
            # last = tickers_df.iloc[start:end].price.mean()
            last = tickers_df.iloc[end-1].price
            tickers.insert_tickers(row.date, coin, last, screen)
            features.update_indicators(row.date, coin, screen)


