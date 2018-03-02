import numpy as np

from sqlalchemy import Table, Column, Integer, String, Float, DateTime

from robot.Extractor import emas, macds, tickers
from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
mkt_trend = Table('Market_trend', meta,
                  Column('coin', String, primary_key=True),
                  Column('date', DateTime, primary_key=True),
                  Column('screen', Integer, primary_key=True),
                  Column('dif_current', Float),
                  Column('dif_base', Float),
                  Column('delta_dif', Float),
                  Column('vote', Integer)
                  )


def insert_trend(coin, date, screen, dif_current, dif_base, delta_dif, vote):
    try:
        clause = mkt_trend.insert().values(coin=coin, date=date, screen=screen,
                                           dif_current=dif_current, dif_base=dif_base,
                                           vote=vote, delta_dif=delta_dif)
        result = con.execute(clause)
    except Exception:
        return


# def trend_market(date, coin):
#     vote = 0
#     n = 4
#
#     ema_df_one = emas.get_emas(n, coin, date, 1)
#     ema_df_two = emas.get_emas(n, coin, date, 2)
#     if len(ema_df_one) < n:
#         return None
#     current_ema20 = ema_df_one.iloc[0].ema20
#     current_ema5 = ema_df_one.iloc[0].ema5
#     dif_current = (current_ema5 - current_ema20)/current_ema20
#
#     base_ema20 = ema_df_one.iloc[len(ema_df_one)-1].ema20
#     base_ema5 = ema_df_one.iloc[len(ema_df_one)-1].ema5
#     dif_base = (base_ema5 - base_ema20)/base_ema20
#     delta_dif = dif_current - dif_base
#     if dif_current > 0.05:
#         if dif_current > dif_base:
#             vote = 1
#     if dif_current < -0.05:
#         if dif_current > dif_base:
#             vote = 1
#     insert_trend(coin, date, 1, dif_current, dif_base, delta_dif, vote)
#
#     return vote


def trend_market(date, coin):
    vote = 0
    n = 3
    ticks = tickers.get_tickers(500, coin, date, 0)
    ticks['log'] = (np.log(ticks['price'] / ticks['price'].shift(-1)))
    vol = np.std(ticks.log) * 50 ** 0.5

    macd_df_one = macds.get_macds(n, coin, date, 1)

    # ema_df_two = emas.get_emas(n, coin, date, 2)
    if len(macd_df_one) < n:
        return None
    theta = [np.arctan(macd_df_one.iloc[1].ema12/macd_df_one.iloc[2].ema12),
             np.arctan(macd_df_one.iloc[0].ema12/macd_df_one.iloc[1].ema12)]
    d_theta = np.log(theta[1]/theta[0])

    current_ema20 = macd_df_one.iloc[0].ema_26
    current_ema5 = macd_df_one.iloc[0].ema12
    dif_current = (current_ema5 - current_ema20) / current_ema20

    base_ema20 = macd_df_one.iloc[len(macd_df_one) - 1].ema_26
    base_ema5 = macd_df_one.iloc[len(macd_df_one) - 1].ema12
    dif_base = (base_ema5 - base_ema20) / base_ema20
    delta_dif = dif_current - dif_base
    if dif_current > 0.05:
        if dif_current > dif_base * (1 + 0.05):
            vote = 1
    if dif_current < -0.05:
        if dif_current > dif_base:
            vote = 1

    #BULL MARKET
    if d_theta >= 0.0025 and vote == 1:
        vote = 1
    elif d_theta <= -0.003 and vote == -1:
        vote = -1
    else:
        #TO SEE HOW THE MARKET GOES
        vote = 0
    insert_trend(coin, date, 1, dif_current, dif_base, d_theta, vote)

    return vote
