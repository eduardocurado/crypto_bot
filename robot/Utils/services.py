from datetime import datetime
import pandas as pd
import pickle
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
        # last = tickers_df.price.mean()
        last = tickers_df.iloc[0].price
        tickers.insert_tickers(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, last, screen)


def execute_order():
    pass


def predict_local_model(data):
    x = pd.DataFrame(columns=['dif_current',
                              'dif_base',
                              'theta_current',
                              'theta_base',
                              'rsi',
                              'ema_dif'])
    x.loc[0] = data
    # load the model from disk
    loaded_model = pickle.load(open('Notebooks/finalized_model.sav', 'rb'))
    return loaded_model.predict(x)[0]
