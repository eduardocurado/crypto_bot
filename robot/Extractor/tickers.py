import pandas as pd
from sqlalchemy.sql import select, and_, or_, not_, desc, asc
from sqlalchemy import Table, Column, Integer, Date, DateTime, String,Float, ForeignKey
from robot.Utils import Initializations

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
tickers = Table('Ticker', meta,
                Column('date', DateTime, primary_key=True),
                Column('coin', String, primary_key=True),
                Column('price', Float),
                Column('volume', Float),
                Column('screen', Integer, primary_key=True)
                )


def get_tickers(n, coin, date, screen):
    s = select([tickers])\
        .where(and_(tickers.c.coin == coin, tickers.c.date <= date, tickers.c.screen == screen))\
        .order_by(desc(tickers.c.date))\
        .limit(n)
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not tickers_df.empty:
        tickers_df.columns = rows.keys()
    return tickers_df


def insert_tickers(date, coin, last, volume, screen):
    try:
        clause = tickers.insert().values(date=date, coin=coin, price=last,volume=volume, screen=screen)
        con.execute(clause)
    except Exception:
        return
        #print("Got error! Ticker")


def get_all_tickers_screen(coin, screen):
    s = select([tickers]) \
        .where(and_(tickers.c.coin == coin, tickers.c.screen == screen)) \
        .order_by(desc(tickers.c.date))
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not tickers_df.empty:
        tickers_df.columns = rows.keys()
    return tickers_df


def get_all_tickers(screen):
    s = select([tickers]) \
        .where(and_(tickers.c.screen == screen)) \
        .order_by(desc(tickers.c.date))
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not tickers_df.empty:
        tickers_df.columns = rows.keys()
    return tickers_df


def get_ticker(coin, date, screen):
    s = select([tickers]) \
        .where(and_(tickers.c.coin == coin, tickers.c.date == date, tickers.c.screen == screen))
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not tickers_df.empty:
        tickers_df.columns = rows.keys()
        return tickers_df
    return tickers_df
