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
                  Column('d_dif', Float),
                  Column('theta_current', Float),
                  Column('theta_base', Float),
                  Column('d_theta', Float),
                  Column('vote', Integer)
                  )


def insert_trend(coin, date, screen, dif_current, dif_base, delta_dif, theta_current, theta_base, d_theta, vote):
    try:
        clause = mkt_trend.insert().values(coin=coin, date=date, screen=screen,
                                           dif_current=dif_current, dif_base=dif_base,
                                           d_dif=delta_dif,
                                           theta_current=theta_current, theta_base=theta_base,
                                           d_theta=d_theta, vote=vote)
        result = con.execute(clause)
    except Exception:
        return


#VESRION USING ONLY EMAS FROM BD (5, 20)
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


#VESRION USING ONLY EMAS FROM MACD (12, 26)
# def trend_market(date, coin):
#     vote = 0
#     n = 3
#     ticks = tickers.get_tickers(500, coin, date, 0)
#     ticks['log'] = (np.log(ticks['price'] / ticks['price'].shift(-1)))
#     vol = np.std(ticks.log) * 50 ** 0.5
#
#     macd_df_one = macds.get_macds(n, coin, date, 1)
#
#     # ema_df_two = emas.get_emas(n, coin, date, 2)
#     if len(macd_df_one) < n:
#         return None
#     # if 0 in macd_df_one.ema12:
#     #     return None
#     theta = [np.log(macd_df_one.iloc[1].ema12/macd_df_one.iloc[2].ema12),
#              np.log(macd_df_one.iloc[0].ema12/macd_df_one.iloc[1].ema12)]
#     d_theta = np.log(theta[1]/theta[0])
#
#     current_ema26 = macd_df_one.iloc[0].ema_26
#     current_ema12 = macd_df_one.iloc[0].ema12
#     dif_current = (current_ema12 - current_ema26) / current_ema26
#
#     base_ema26 = macd_df_one.iloc[len(macd_df_one) - 1].ema_26
#     base_ema12 = macd_df_one.iloc[len(macd_df_one) - 1].ema12
#     dif_base = (base_ema12 - base_ema26) / base_ema26
#     delta_dif = dif_current - dif_base
#     if dif_current > 0.05:
#         if dif_current > dif_base * (1 + 0.05):
#             vote = 1
#
#     if dif_current < -0.05:
#         if dif_current > dif_base:
#             vote = 1
#
#     #BULL MARKET
#     if d_theta >= 0 and vote == 1:
#         vote = 1
#     elif d_theta <= 0 and vote == -1:
#         vote = -1
#     else:
#         #TO SEE HOW THE MARKET GOES
#         vote = 0
#     insert_trend(coin, date, 1, dif_current, dif_base, d_theta, vote)
#
#     return vote


#VESRION USING FFT FROM TICK SCREEN ONE
def trend_market(date, coin):
    from scipy.fftpack import ifft, fft
    from math import atan

    df = tickers.get_tickers(300, coin, date, 1)#TODO Change screen test
    df = df[df.date < date]
    data = df.price

    theta_vote = 0
    if len(df) < 4:
        vote = 0
        return
    else:
        yf = fft(data)
        wn = 18
        yf[wn:-wn] = 0
        iY = ifft(yf).real[::-1]
        theta = [atan((iY[1] - iY[2]) / 48),
                 atan((iY[2] - iY[3]) / 48)]
        # theta = [np.log(iY[2] / iY[3]),
        #          np.log(iY[2] / iY[3])]

        # MARKET TREND LOG RETURN -> price_current / price_base
        # BULL MARKET
        # d_theta = np.log(iY[0]/iY[1])
        # if d_theta >= 0:
        #     theta_vote = 1
        # elif d_theta <= 0:
        #     theta_vote = -1
        # else:
        #     # TO SEE HOW THE MARKET GOES
        #     theta_vote = 0
        threshold = 0
        if theta[0] > 0 and theta[1] > 0:
            d_theta = np.log(theta[0] / theta[1])
            if d_theta > threshold:
                theta_vote = 1
        elif theta[0] > 0 > theta[1]:
            d_theta = np.log(theta[0] / abs(theta[1]))
            if d_theta <= -threshold:
                theta_vote = 1
        elif theta[0] < 0 < theta[1]:
            d_theta = np.log(abs(theta[0]) / theta[1])
            theta_vote = 0
        elif theta[0] < 0 and theta[1] < 0:
            d_theta = np.log(abs(theta[0])/abs(theta[1]))
            if d_theta <= -threshold:
                theta_vote = 1


    n = 3
    # ticks = tickers.get_tickers(500, coin, date, 0)
    # ticks['log'] = (np.log(ticks['price'] / ticks['price'].shift(-1)))
    # vol = np.std(ticks.log) * 50 ** 0.5

    macd_df_one = macds.get_macds(n, coin, date, 1)

    # ema_df_two = emas.get_emas(n, coin, date, 2)
    if len(macd_df_one) < n:
        return None

    vote_macd = 0
    vote = 0

    current_ema26 = macd_df_one.iloc[0].ema_26
    current_ema12 = macd_df_one.iloc[0].ema12
    dif_current = np.log(current_ema12/current_ema26)

    base_ema26 = macd_df_one.iloc[len(macd_df_one) - 1].ema_26
    base_ema12 = macd_df_one.iloc[len(macd_df_one) - 1].ema12
    dif_base = np.log(base_ema12/base_ema26)

    delta_dif = 0

    if (dif_current > 0) and (dif_base > 0):
        delta_dif = np.log(dif_current/dif_base)
        if delta_dif > 0:
            vote_macd = 1
    elif (dif_current < 0) and (dif_base > 0):
        vote_macd = -1
    elif (dif_current < 0) and (dif_base < 0):
        delta_dif = np.log(abs(dif_current/dif_base))
        if delta_dif < 0:
            vote_macd = 1
    elif (dif_current > 0) and (dif_base < 0):
        vote_macd = 1

    if vote_macd == theta_vote == 1:
        vote = 1
    elif vote_macd == theta_vote == -1:
        vote = -1

    insert_trend(coin, date, 1, dif_current, dif_base, delta_dif, theta[0], theta[1], d_theta, vote)
    return vote
