import pandas as pd
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_

from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
boillinger = Table('Boillinger', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('upper_band', Float),
    Column('lower_band', Float),
    Column('sma20', Float),
    Column('height', Float),
    Column('screen', Integer, primary_key=True)
)


def insert_boillingers(date, coin, upper_band, lower_band, sma20, height, screen):
    try:
        clause = boillinger.insert().values(date=date, coin=coin, upper_band=upper_band,
                                            lower_band=lower_band, sma20=sma20, height=height, screen=screen)
        result = con.execute(clause)
        #             print('Done.')
        return
    except Exception:
        print("Got error! Boillinger" + repr(Exception))


def get_boillinger(n, coin, date, screen):
    s = select([boillinger]).\
        where(and_(boillinger.c.coin == coin, boillinger.c.date <= date, boillinger.c.screen == screen))\
        .order_by(boillinger.c.date.desc()).limit(n)
    rows = con.execute(s)
    boillinger_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not boillinger_df.empty:
        boillinger_df.columns = rows.keys()
    return boillinger_df
