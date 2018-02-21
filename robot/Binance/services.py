from datetime import datetime

from poloniex import Poloniex

from robot.Extractor import tickers


def feed_data(coin):
    polo = Poloniex()
    intermediate_data = polo('returnTicker')[coin]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last = intermediate_data['last']
    coin = 'BTC'
    tickers.insert_tickers(date, coin, last, 0)
    return last, date


def triple_screen(n, coin, screen):
    tickers_df = tickers.get_tickers(n, coin, datetime.now(), 0)
    if len(tickers_df) >= n:
        last = tickers_df.price.mean()
        tickers.insert_tickers(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, last, screen)
