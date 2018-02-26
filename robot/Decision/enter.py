from sqlalchemy import Table, Column, Integer, String, Float, DateTime

from robot.Decision import exit
from robot.Extractor import signals, emas
from robot.Indicators import Ingestion
from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
mkt_trend = Table('Market_trend', meta,
                  Column('coin', String, primary_key=True),
                  Column('date', DateTime, primary_key=True),
                  Column('screen', String, primary_key=True),
                  Column('dif_current', Float),
                  Column('dif_base', Float),
                  Column('vote', Integer)
                  )


def insert_trend(coin, date, screen, dif_current, dif_base, vote):
    try:
        clause = mkt_trend.insert().values(coin=coin, date=date, screen=screen,
                                           dif_current=dif_current, dif_base=dif_base, vote=vote)
        result = con.execute(clause)
    except Exception:
        return


def trend_market(date, coin):
    vote = 0
    ema_df_one = emas.get_emas(5, coin, date, 1)
    ema_df_two = emas.get_emas(5, coin, date, 2)
    if len(ema_df_one) < 2:
        return None

    current_ema20 = ema_df_one.iloc[0].ema20
    current_ema5 = ema_df_one.iloc[0].ema5
    dif_current = current_ema5 - current_ema20

    base_ema20 = ema_df_one.iloc[1].ema20
    base_ema5 = ema_df_one.iloc[1].ema5
    dif_base = base_ema5 - base_ema20

    if dif_current > 0:
        if dif_base <= 0:
            vote = 1
        elif dif_current > dif_base:
            vote = 1

    if dif_current < 0:
        if dif_base >= 0:
            vote = -1
        elif abs(dif_current) > abs(dif_base):
            vote = -1
    insert_trend(coin, date, 1, dif_current, dif_base, vote)

    return vote


def strategy_one(coin, date, tick):
    entry_sign = Ingestion.get_ema_vote(date, coin, 1)
    trend_screen_one = trend_market(date, coin)
    # trend_screen_two = trend_market(date, coin, 2)
    if trend_screen_one == 1 and entry_sign == 1:
        signals.insert_signal(date, coin, tick, 'BUY', 'ENTER_ONE')
        return {'signal': 'BUY',
                'take_profit': tick * (1 + 0.2),
                'stop_loss': tick * (1 - 0.1)}
    # elif vote_screen_one == -1 and vote_screen_two == -1 and entry_sign == -1:
    #     signals.insert_signal(date, coin, tick, 'SELL', 'ENTER_ONE')
    #     return {'signal': 'SELL',
    #             'take_profit': tick * (1 - 0.15),
    #             'stop_loss': tick * (1 - 0.05)}
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_ONE')
        return None


# def trend_market(date, coin, screen):
#     vote = 0
#     ema_df = emas.get_emas(5, coin, date, screen)
#     if len(ema_df) < 2:
#         return None
#     current_ema20 = ema_df.iloc[0].ema20
#     current_ema5 = ema_df.iloc[0].ema5
#     base_ema20 = ema_df.iloc[1].ema20
#     base_ema5 = ema_df.iloc[1].ema5
#     dif_current = current_ema5 - current_ema20
#     dif_base = base_ema5 - base_ema20
#     dif5 = current_ema5 - base_ema5
#     # dif20 = current_ema20 - base_ema20
#     if dif_current > 0 and dif_base > 0 and dif5 > 0:
#         vote = 1
#     elif dif_current < 0 and dif_base < 0 and dif5 < 0:
#         vote = -1
#     insert_trend(coin, date, screen, dif_current, dif_base, vote)
#
#     return vote


def strategy_two(coin, date, tick):
    trend_screen_one = trend_market(date, coin)
    # trend_screen_two = trend_market(date, coin, 2)
    ema = emas.get_emas(1, coin, date, 1)
    if not ema.empty:
        exit_points = exit.get_exit_channel(coin, date, tick, 1)
        if ema.iloc[0].ema20 > tick > ema.iloc[0].ema20 * (1 - 0.1) and trend_screen_one == 1:
            signals.insert_signal(date, coin, tick, 'BUY', 'ENTER_TWO')
            return {'signal': 'BUY',
                    'take_profit': exit_points.get('take_profit'),
                    'stop_loss': exit_points.get('stop_loss')}
        # elif ema.iloc[0].ema20 < tick < ema.iloc[0].ema20 * (1 + 0.1) and trend_two == -1 and trend_one == -1:
        #     signals.insert_signal(date, coin, tick, 'SELL', 'ENTER_TWO')
        #     return {'signal': 'SELL',
        #             'take_profit': exit_points.get('take_profit'),
        #             'stop_loss': exit_points.get('stop_loss')}
        else:
            signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
            return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
        return None
