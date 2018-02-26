import pandas as pd
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_

from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
signal = Table('Signal', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('tick', Float),
    Column('signal', String, primary_key=True),
    Column('signal_source', String, primary_key=True)
)


def insert_signal(date, coin, tick, signal_screen, signal_source):
    try:
        clause = signal.insert().values(date=date,
                                        coin=coin,
                                        tick=tick,
                                        signal=signal_screen,
                                        signal_source=signal_source)
        result = con.execute(clause)
        return
    except Exception:
        return
        #print("Got error! Signal" + repr(Exception))


def get_signal(n, coin, date):
    s = select([signal]).\
        where(and_(signal.c.coin == coin, signal.c.date <= date))\
        .order_by(signal.c.date.desc())\
        .limit(n)
    rows = con.execute(s)
    signal_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not signal_df.empty:
        signal_df.columns = rows.keys()
    return signal_df
