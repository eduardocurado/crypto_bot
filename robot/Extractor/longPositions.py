import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from sqlalchemy.sql import select, and_, desc

from robot.Utils import Initializations
from robot.Decision import features
from robot.Extractor import orders_book, shortPositions


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
long_positions = Table('Long', meta,
                       Column('id_position', Integer, primary_key=True),
                       Column('coin', String, primary_key=True),
                       Column('size_position', Float),
                       Column('date_ask', DateTime),
                       Column('ask', Float),
                       Column('date_settlement', DateTime),
                       Column('settlement', Float),
                       Column('take_profit', Float),
                       Column('stop_loss', Float),
                       Column('exit_price', Float),
                       Column('status', String)
                       )


def get_longs(coin, id_position):
    s = select([long_positions])\
        .where(and_(long_positions.c.coin == coin,
                    long_positions.c.id_position == id_position))\
        .order_by(desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def get_all_longs(coin):
    s = select([long_positions]) \
        .where(and_(long_positions.c.coin == coin)) \
        .order_by(desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def get_positions(coin, status):
    s = select([long_positions]) \
        .where(and_(long_positions.c.coin == coin,
                    long_positions.c.status == status))\
        .order_by(desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def insert_long(id_position, coin, size_position, date_ask, ask, date_settlement, settlement, take_profit,
                stop_loss, status):
    try:
        clause = long_positions.insert().values(id_position=id_position,
                                                coin=coin,
                                                size_position=size_position,
                                                date_ask=date_ask,
                                                ask=ask,
                                                date_settlement=date_settlement,
                                                settlement=settlement,
                                                take_profit=take_profit,
                                                stop_loss=stop_loss,
                                                status=status)
        result = con.execute(clause)
    except Exception:
        return


def enter_positions(id_position, coin, size_position, date_ask, tick, take_profit, stop_loss):
    orders_book.create_order()
    insert_long(id_position, coin, size_position, date_ask, tick, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                float(tick), take_profit, stop_loss, 'active')


def close_positions(id_position, coin, tick):
    try:
        clause = long_positions.update(). \
            where(and_(long_positions.c.id_position == id_position,
                       long_positions.c.coin == coin)). \
            values(status='closed',
                   exit_price=tick)
        result = con.execute(clause)
    except Exception:
        print('Got error Close')


def update_position_stop_loss(id_position, coin, stop_loss):
    try:
        clause = long_positions.update(). \
            where(and_(long_positions.c.id_position == id_position,
                       long_positions.c.coin == coin)). \
            values(stop_loss=stop_loss)
        result = con.execute(clause)
    except Exception:
        print('Got error Close')


def exit_positions(exits):
    for e in exits:
        date_ask = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ordered = orders_book.create_order()
        ordered = dict({'date_settlement': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'settlement': (e.get('exit_price'))})

        long_id = get_longs(e.get('coin'), e.get('id')).iloc[0]
        print(np.log(ordered.get('settlement')/long_id.settlement))
        close_positions(e.get('id'),
                        e.get('coin'),
                        e.get('exit_price')
                        )

        shortPositions.insert_short(e.get('id'),
                                    e.get('coin'),
                                    e.get('size_position'),
                                    e.get('ask_date'),
                                    e.get('exit_price'),
                                    ordered.get('date_settlement'),
                                    ordered.get('settlement'),
                                    e.get('source'))


def update_take_profit():
    # update open positions
    pass


def update_stop_loss(coin, tick):
    # update open positions
    open_positions = get_positions(coin, 'active')
    if not open_positions.empty:
        for index, row in open_positions.iterrows():
            new_stop_loss = max(tick * (1 - 0.05), row.stop_loss)
            if new_stop_loss > row.stop_loss:
                print('Updating Stop Loss')
                update_position_stop_loss(row.id_position, coin, new_stop_loss)
