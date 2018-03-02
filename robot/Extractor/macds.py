import pandas as pd
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_, desc

from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
macd = Table('Macd', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('ema12', Float),
    Column('ema_26', Float),
    Column('macd_line', Float),
    Column('signal_line', Float),
    Column('histogram', Float),
    Column('screen', Integer, primary_key=True)
)


def get_macds(n, coin, date, screen):
    s = select([macd])\
        .where(and_(macd.c.coin == coin, macd.c.date <= date, macd.c.screen == screen))\
        .order_by(desc(macd.c.date)).limit(
        n)
    rows = con.execute(s)
    macd_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not macd_df.empty:
        macd_df.columns = rows.keys()
    return macd_df


def insert_macd(date, coin, ema12, ema26, macd_line, signal_line, histogram, screen):
    try:
        clause = macd.insert().values(date=date, coin=coin, ema12=ema12, ema_26=ema26,
                                  macd_line=macd_line, signal_line=signal_line, histogram=histogram, screen=screen)
        result = con.execute(clause)
    except Exception:
        return
