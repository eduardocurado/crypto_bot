import pandas as pd
from datetime import datetime
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_, desc

from robot.Utils import Initializations
from robot.Decision import features
from robot.Extractor import orders_book, shortPositions


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
balances = Table('Balance', meta,
                 Column('date', DateTime, primary_key=True),
                 Column('coin', String, primary_key=True),
                 Column('size_position', Float)
                 )


def insert_balance(date, coin, size_positions):
    try:
        clause = balances.insert().values(date=date,
                                          coin=coin,
                                          size_positions=size_positions)
        result = con.execute(clause)
    except Exception:
        return


def get_balances(coin, date):
    s = select([balances]) \
        .where(and_(balances.c.coin == coin,
                    balances.c.date <= date))\
        .order_by(desc(balances.c.date_ask))
    rows = con.execute(s)
    balances_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not balances_df.empty:
        balances_df.columns = rows.keys()
    return balances_df


