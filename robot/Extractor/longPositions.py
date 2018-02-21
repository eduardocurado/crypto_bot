import pandas as pd
from datetime import datetime
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_, desc

from robot.Utils import Initializations
from robot.Decision import features
from robot.Extractor import orders_book


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
long_positions = Table('Long', meta,
                       Column('id_position', Integer, primary_key = True),
                       Column('coin', String, primary_key = True),
                       Column('date_ask', DateTime),
                       Column('ask', Float),
                       Column('date_settlement', DateTime),
                       Column('settlement', Float),
                       Column('take_profit', Float),
                       Column('stop_loss', Float),
                       Column('status', String)
                       )


def get_longs(n, coin, date):
    s = select([long_positions])\
        .where(and_(long_positions.c.coin == coin, long_positions.c.date <= date))\
        .order_by(desc(long_positions.c.date_ask)).limit(n)
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def get_all_longs(coin, screen):
    s = select([long_positions]) \
        .where(and_(long_positions.c.coin == coin, long_positions.c.screen == screen)) \
        .order_by(
        desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def get_open_positions(coin):
    s = select([long_positions]) \
        .where(and_(long_positions.c.coin == coin, long_positions.c.status == 'active')) \
        .order_by(desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def insert_long(id_position, coin, date_ask, ask, date_settlement, settlement, take_profit, stop_loss, status):
    try:
        clause = long_positions.insert().values(id_position=id_position, coin=coin, date_ask=date_ask, ask=ask,
                                                date_settlement=date_settlement, settlement=settlement,
                                                take_profit=take_profit, stop_loss=stop_loss, status=status)
        result = con.execute(clause)
    except Exception:
        print('Got error Long')


def exit_positions(exits):
    #for each exits
    orders_book.create_order()
    features.update_position()
    features.update_balance()
    pass


def enter_positions(id_position, coin, date_ask, tick):
    orders_book.create_order()
    insert_long(id_position, coin, date_ask, tick, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                float(tick)+0.001, float(tick)+0.01, float(tick)-0.001, 'active')
