from sqlalchemy import Table, Column, Integer, String, Float, DateTime

from robot.Extractor import emas
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


def trend_market(date, coin):
    vote = 0
    ema_df_one = emas.get_emas(5, coin, date, 1)
    ema_df_two = emas.get_emas(5, coin, date, 2)
    if len(ema_df_one) < 2:
        return None
    current_ema20 = ema_df_one.iloc[0].ema20
    current_ema5 = ema_df_one.iloc[0].ema5
    dif_current = (current_ema5 - current_ema20)/current_ema20

    base_ema20 = ema_df_one.iloc[1].ema20
    base_ema5 = ema_df_one.iloc[1].ema5
    dif_base = (base_ema5 - base_ema20)/base_ema20
    delta_dif = dif_current - dif_base
    if dif_current > 0.05:
        if delta_dif > 0:
            vote = 1

    if dif_current < 0.05:
        if dif_base > 0:
            vote = -1
        elif delta_dif < 0:
            vote = -1
    insert_trend(coin, date, 1, dif_current, dif_base, delta_dif, vote)

    return vote
