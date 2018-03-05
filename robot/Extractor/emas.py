import pandas as pd
from sqlalchemy.sql import select, and_, or_, not_, desc, asc
from sqlalchemy import Table, Column, Integer, Date, DateTime, String,Float, ForeignKey
from robot.Utils import Initializations, Plots


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
ema = Table('Ema', meta,
            Column('date', DateTime, primary_key = True),
            Column('coin', String, primary_key = True),
            Column('ema5', Float),
            Column('ema20', Float),
            Column('ema5_theta', Float),
            Column('ema20_theta', Float),
            Column('screen', Integer, primary_key=True)
)


def insert_emas(date, coin, ema5, ema20, screen):
    try:
        clause = ema.insert().values(date=date, coin=coin, ema5=ema5, ema20=ema20, screen=screen)
        result = con.execute(clause)
        #             print('Done.')
        return
    except Exception:
        print("Got error! EMA" + repr(Exception))
        return


def get_emas(n, coin, date, screen):
    s = select([ema])\
        .where(and_(ema.c.coin == coin, ema.c.date <= date, ema.c.screen == screen))\
        .order_by(ema.c.date.desc()).limit(n)
    rows = con.execute(s)
    ema_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not ema_df.empty:
        ema_df.columns = rows.keys()
    return ema_df
