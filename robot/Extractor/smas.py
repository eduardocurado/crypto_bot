import pandas as pd
from sqlalchemy.sql import select, and_, or_, not_, desc, asc
from sqlalchemy import Table, Column, Integer, Date, DateTime, String,Float, ForeignKey
from robot.Utils import Initializations, Plots


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
sma = Table('Sma', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('sma5', Float),
    Column('sma20', Float),
    Column('sma5_theta', Float),
    Column('sma20_theta', Float),
    Column('screen', Integer, primary_key=True)
)


def get_smas(n, coin, date, screen):
    s = select([sma])\
        .where(and_(sma.c.coin == coin, sma.c.date <= date, sma.c.screen==screen))\
        .order_by(sma.c.date.desc()).limit(n)
    rows = con.execute(s)
    sma_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not sma_df.empty:
        sma_df.columns = rows.keys()
    return sma_df


def insert_smas(date, coin, sma5, sma20, sma5_theta, screen):
    try:
        clause = sma.insert().values(date=date, coin=coin, sma5=sma5, sma20=sma20,
                                     sma5_theta=sma5_theta, screen=screen)
        con.execute(clause)
        return
    except Exception:
        print("Got error! SMA" + repr(Exception))
