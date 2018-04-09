from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import Column, DateTime, Float, Integer, String, Table, desc
from sqlalchemy.sql import and_, select

from robot.Extractor import macds, rsis, tickers, smas
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
                  Column('max_rel', Float),
                  Column('min_rel', Float),
                  Column('log_ret', Float),
                  Column('log_ret_p', Float),
                  Column('log_ret_t_1', Float),
                  Column('histogram', Float),
                  Column('ema_dif', Float),
                  Column('rsi', Float),
                  Column('dif_sma', Float),
                  Column('max_growth_p', Float),
                  Column('obv', Float),
                  Column('strength', Float),
                  Column('vote', Integer)
                  )


def insert_trend(coin, date, screen, dif_current, dif_base, delta_dif, theta_current, theta_base,
                 d_theta, long_dif, max_price, min_price, max_rel, min_rel, log_ret, log_ret_p,
                 log_ret_t_1, histogram, ema_dif, rsi, dif_sma, max_growth_p, obv, strength, vote):
    # try:
    clause = mkt_trend.insert().values(coin=coin, date=date, screen=screen,
                                       dif_current=dif_current, dif_base=dif_base,
                                       d_dif=delta_dif, long_dif=long_dif,
                                       theta_current=theta_current, theta_base=theta_base,
                                       max_price=max_price, min_price=min_price,
                                       d_theta=d_theta, max_rel=max_rel, min_rel=min_rel,
                                       log_ret=log_ret, log_ret_p=log_ret_p,
                                       log_ret_t_1=log_ret_t_1, histogram=histogram,
                                       ema_dif=ema_dif, rsi=rsi, dif_sma=dif_sma,
                                       max_growth_p=max_growth_p, obv=obv, strength=strength,
                                       vote=vote)
    result = con.execute(clause)
    # except Exception:
    #     return


def get_mkt_trends(n, coin, date, screen):
    s = select([mkt_trend]) \
        .where(
        and_(mkt_trend.c.coin == coin, mkt_trend.c.date <= date, mkt_trend.c.screen == screen)) \
        .order_by(desc(mkt_trend.c.date)) \
        .limit(n)
    rows = con.execute(s)
    mkt_trend_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not mkt_trend_df.empty:
        mkt_trend_df.columns = rows.keys()
    return mkt_trend_df


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


def update_obv(coin, date, screen, obv):
    try:
        clause = mkt_trend.update(). \
            where(and_(mkt_trend.c.date == date,
                       mkt_trend.c.coin == coin,
                       mkt_trend.c.screen == screen)). \
            values(obv=obv)
        result = con.execute(clause)
    except Exception:
        print('Got error OBV')


def get_max_growth(tickers_filtered, base_price):
    max_growth = 0
    max_loss = 0
    for i, r in tickers_filtered.iterrows():
        g = np.log(r.price / base_price)
        max_growth = g if g > max_growth else max_growth
        max_loss = g if g < max_loss else max_loss
    return max_growth, max_loss


def get_max_min_change(coin, tickers_df_two_c):
    tickers_df_two_c = tickers_df_two_c[::-1]
    delta_t = 1
    date_now = tickers_df_two_c.iloc[0].date
    last_date_now = date_now + timedelta(hours=24)
    base_date = date_now
    base_price = tickers_df_two_c.iloc[0].price
    print(base_date)
    print(last_date_now)
    tickers_one = tickers.get_all_tickers_screen(coin, 0)
    t = tickers_one[(tickers_one['date'] >= base_date) & (tickers_one['date'] <= last_date_now)]
    max_growth, max_loss = get_max_growth(t, base_price)
    date = datetime.strftime(base_date, '%Y-%m-%d %H:%M:%S')
    return max_growth, max_loss


def get_max_min(coin, date):
    ticker_df = tickers.get_all_tickers_screen(coin, 0)[::-1]
    date_now = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    last_date_now = date_now - timedelta(hours=12)
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


def trend_market(date, coin, tick, ema_dif):
    # strength_ema
    from scipy.fftpack import ifft, fft
    from math import atan

    print('Current Date')
    print(date)
    # 300 segundos = 5 min

    # 600 * 4h = 2400 h / 24 h = 50 dias
    price_df = tickers.get_tickers(600, coin, date, 1)
    df = price_df[price_df.date <= date]
    data = df.price
    price_df = price_df[::-1]
    # 300 * 4h = 1200 h / 24 h = 50 dias
    if len(df) < 300:
        vote = 0
        return None
    else:
        max_growth, max_loss = get_max_min_change(coin, df)
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
    sma_one = smas.get_smas(n, coin, date, 1)
    mkttrend_df = get_mkt_trends(6, coin, date, 1)
    if len(macd_df_one) < n and len(macd_df_two) < n:
        return None
    macd_df_one = macd_df_one[::-1]
    macd_df_two = macd_df_two[::-1]
    sma_one = sma_one[::-1]
    mkttrend_df = mkttrend_df[::-1]
    if len(mkttrend_df) >= 2:
        max_growth_p = np.nan
        obv_p = mkttrend_df.iloc[0].obv
        volume = price_df.iloc[0].volume
        p_price = price_df.iloc[1].price
        price = price_df.iloc[0].price
        if price > p_price:
            obv = obv_p + volume
        elif price < p_price:
            obv = obv_p - volume
        else:
            obv = obv_p
        if len(mkttrend_df) == 6:
            prev = mkttrend_df.iloc[5]
            last_prev_date = prev.date + timedelta(hours=24)
            print(prev.date)
            print(last_prev_date)
            max_growth_p = mkttrend_df.iloc[5].max_growth
    # SET FIRST OBV: MKT TREND = 0 | 1
    elif len(mkttrend_df) == 1:
        max_growth_p = np.nan
        obv_p = mkttrend_df.iloc[0].obv
        volume = price_df.iloc[0].volume
        p_price = price_df.iloc[1].price
        price = price_df.iloc[0].price
        if price > p_price:
            obv = obv_p + volume
        elif price < p_price:
            obv = obv_p - volume
        else:
            obv = obv_p
    else:
        obv = 0
        max_growth_p = np.nan

    current_ema26 = macd_df_one.iloc[1].ema_26
    current_ema12 = macd_df_one.iloc[1].ema12
    dif_current = current_ema12 - current_ema26

    base_ema26 = macd_df_one.iloc[0].ema_26
    base_ema12 = macd_df_one.iloc[0].ema12
    dif_base = base_ema12 - base_ema26

    delta_dif = (dif_current - dif_base) / dif_base

    long_current_ema26 = macd_df_two.iloc[1].ema_26
    long_current_ema12 = macd_df_two.iloc[1].ema12
    long_dif_current = long_current_ema12 - long_current_ema26

    current_sma5 = sma_one.iloc[0].sma5
    current_sma20 = sma_one.iloc[0].sma20
    dif_sma = current_sma5 - current_sma20

    rsi = rsi_sign(coin, date)/100

    max_price, min_price = get_max_min(coin, date)

    max_rel = np.log(max_price / tick)
    min_rel = np.log(min_price / tick)

    log_ret = np.log(price_df.iloc[0].price) - np.log(price_df.iloc[1].price)
    log_ret_t_1 = np.log(price_df.iloc[1].price) - np.log(price_df.iloc[2].price)
    log_ret_p = np.log(price_df.iloc[0].price) - np.log(price_df.iloc[2].price)
    histogram = macd_df_one.iloc[0].histogram
    strength = (price_df.iloc[0].price - price_df.iloc[1].price) * price_df.iloc[0].volume

    data = [dif_current, dif_base, theta[0], theta[1], rsi, ema_dif]
    vote = services.predict_local_model(data)
    insert_trend(coin, date, 1, dif_current, dif_base, delta_dif,
                 theta[0], theta[1], d_theta, long_dif_current,
                 max_price, min_price, max_rel, min_rel, log_ret,
                 log_ret_p, log_ret_t_1, histogram, ema_dif, rsi,
                 dif_sma, max_growth_p, obv, strength, vote)
    update_max_growth(coin, date, 1, max_growth, max_loss)
    return vote
