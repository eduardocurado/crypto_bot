import pandas as pd
from datetime import datetime
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_, desc

from robot.Utils import Initializations
from robot.Decision import features
from robot.Extractor import orders_book

con, meta = Initializations.connect_db('postgres', '', 'robotdb')
short_positions = Table('Short', meta,
                        Column('id_position', Integer, primary_key=True),
                        Column('coin', String, primary_key=True),
                        Column('size', Float),
                        Column('date_ask', DateTime),
                        Column('ask', Float),
                        Column('date_settlement', DateTime),
                        Column('settlement', Float),
                        Column('source', String)
                        )


def get_shorts(n, coin, date):
    s = select([short_positions]) \
        .where(and_(short_positions.c.coin == coin, short_positions.c.date <= date)) \
        .order_by(desc(short_positions.c.date_ask)).limit(n)
    rows = con.execute(s)
    short_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not short_positions_df.empty:
        short_positions_df.columns = rows.keys()
    return short_positions_df


def get_all_shorts(coin, screen):
    s = select([short_positions]) \
        .where(and_(short_positions.c.coin == coin, short_positions.c.screen == screen)) \
        .order_by(
        desc(short_positions.c.date_ask))
    rows = con.execute(s)
    short_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not short_positions_df.empty:
        short_positions_df.columns = rows.keys()
    return short_positions_df


def insert_short(id_position, coin, size, date_ask, ask, date_settlement, settlement, source):
    try:
        clause = short_positions.insert().values(id_position=id_position, coin=coin, size=size,date_ask=date_ask, ask=ask,
                                                 date_settlement=date_settlement, settlement=settlement,
                                                 source=source)
        result = con.execute(clause)
    except Exception:
        print('Got error Short')
