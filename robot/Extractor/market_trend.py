from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import Column, DateTime, Float, Integer, String, Table
from sqlalchemy.sql import and_

from robot.Extractor import macds, rsis, tickers
from robot.Utils import Initializations
from robot.Utils import services

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
mkt_trend = Table('Market_trend', meta,
                  Column('coin', String, primary_key=True),
                  Column('date', DateTime, primary_key=True),
                  Column('screen', Integer, primary_key=True),
                  Column('dif_current', Float),
                  Column('dif_base', Float),
                  Column('d_dif', Float),
                  Column('theta_current', Float),
                  Column('theta_base', Float),
                  Column('d_theta', Float),
                  Column('long_dif', Float),
                  Column('max_growth', Float),
                  Column('max_loss', Float),
                  Column('max_price', Float),
                  Column('min_price', Float),
                  Column('vote', Integer)
                  )


def insert_trend(coin, date, screen, dif_current, dif_base, delta_dif, theta_current, theta_base, d_theta, long_dif,
                 max_price, min_price, vote):
    try:
        clause = mkt_trend.insert().values(coin=coin, date=date, screen=screen,
                                           dif_current=dif_current, dif_base=dif_base,
                                           d_dif=delta_dif,
                                           long_dif=long_dif,
                                           theta_current=theta_current, theta_base=theta_base,
                                           max_price=max_price, min_price=min_price,
                                           d_theta=d_theta, vote=vote)
        result = con.execute(clause)
    except Exception:
        return


def update_max_growth(coin, date, screen, max_growth, max_loss):
    try:
        clause = mkt_trend.update(). \
            where(and_(mkt_trend.c.date == date,
                       mkt_trend.c.coin == coin,
                       mkt_trend.c.screen == screen)). \
            values(max_growth=max_growth,
                   max_loss=max_loss)
        result = con.execute(clause)
    except Exception:
        print('Got error Max Growth')


def get_max_growth(tickers_filtered, base_price):
    max_growth = 0
    max_loss = 0
    for i, r in tickers_filtered.iterrows():
        g = np.log(r.price/base_price)
        max_growth = g if g > max_growth else max_growth
        max_loss = g if g < max_loss else max_loss
    return max_growth, max_loss


def get_max_min_change(coin, tickers_df_two_c):
    tickers_df_two_c = tickers_df_two_c[::-1]
    delta_t = 6
    base_date = tickers_df_two_c.iloc[delta_t].date
    last_date = tickers_df_two_c.iloc[0].date
    print('Base Date for Max Change')
    print(base_date)
    print('Last Date for Max Change')
    print(last_date)
    base_price = tickers_df_two_c.iloc[delta_t].price
    tickers_one = tickers.get_all_tickers_screen(coin, 0)
    t = tickers_one[(tickers_one['date'] >= base_date) & (tickers_one['date'] < last_date)]
    max_growth, max_loss = get_max_growth(t, base_price)
    update_max_growth(coin, base_date, 1, max_growth, max_loss)
    return max_growth


def get_max_min(coin, date):
    ticker_df = tickers.get_all_tickers_screen(coin, 0)[::-1]
    date_now = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    last_date_now = date_now - timedelta(hours=24)
    if len(ticker_df):
        _between = ticker_df[(ticker_df['date'] >= last_date_now) & (ticker_df['date'] <= date_now)]
        max_price, min_price = np.max(_between['price']), np.min(_between['price'])
        return max_price, min_price
    return None, None


def rsi_sign(coin, date):
    rsi_df = rsis.get_rsis(1, coin, date, 1)
    if rsi_df.empty:
        return None
    rsi = rsi_df.rsi[0]
    return rsi


def trend_market(date, coin, ema_dif):
    from scipy.fftpack import ifft, fft
    from math import atan
    print('Date')
    print(date)
    # 300 segundos = 5 min

    # 600 * 4h = 2400ç h / 24 h = 50 dias
    df = tickers.get_tickers(600, coin, date, 1)
    df = df[df.date < date]
    data = df.price
    # 300 * 4h = 1200 h / 24 h = 50 dias
    if len(df) < 300:
        vote = 0
        return None
    else:
        get_max_min_change(coin, df)
        yf = fft(data)
        wn = 18
        yf[wn:-wn] = 0
        iY = ifft(yf).real[::-1]
        theta = [atan((iY[0] - iY[1]) / 48),
                 atan((iY[1] - iY[2]) / 48)]

        d_theta = (theta[0] - theta[1]) / theta[1]

    n = 2
    macd_df_one = macds.get_macds(n, coin, date, 1)
    macd_df_two = macds.get_macds(n, coin, date, 2)
    if len(macd_df_one) < n and len(macd_df_two) < n:
        return None

    current_ema26 = macd_df_one.iloc[1].ema_26
    current_ema12 = macd_df_one.iloc[1].ema12
    dif_current = current_ema12 - current_ema26
    base_ema26 = macd_df_one.iloc[0].ema_26
    base_ema12 = macd_df_one.iloc[0].ema12
    dif_base = base_ema12 - base_ema26
    delta_dif = (dif_current - dif_base)/dif_base

    long_current_ema26 = macd_df_two.iloc[1].ema_26
    long_current_ema12 = macd_df_two.iloc[1].ema12
    long_dif_current = long_current_ema12 - long_current_ema26

    rsi = rsi_sign(coin, date)
    max_price, min_price = get_max_min(coin, date)
    data = [dif_current, dif_base, theta[0], theta[1], rsi/100, ema_dif]
    vote = services.predict_local_model(data)

    insert_trend(coin, date, 1, dif_current, dif_base, delta_dif,
                 theta[0], theta[1], d_theta, long_dif_current,
                 max_price, min_price,
                 vote)
    return vote
