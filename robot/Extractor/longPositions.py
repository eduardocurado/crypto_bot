import pandas as pd
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
                       Column('size', Float),
                       Column('date_ask', DateTime),
                       Column('ask', Float),
                       Column('date_settlement', DateTime),
                       Column('settlement', Float),
                       Column('take_profit', Float),
                       Column('stop_loss', Float),
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
        .where(and_(long_positions.c.coin == coin, long_positions.c.status == status))\
        .order_by(desc(long_positions.c.date_ask))
    rows = con.execute(s)
    long_positions_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not long_positions_df.empty:
        long_positions_df.columns = rows.keys()
    return long_positions_df


def insert_long(id_position, coin, size, date_ask, ask, date_settlement, settlement, take_profit,
                stop_loss, status):
    try:
        clause = long_positions.insert().values(id_position=id_position,
                                                coin=coin,
                                                size=size,
                                                date_ask=date_ask,
                                                ask=ask,
                                                date_settlement=date_settlement,
                                                settlement=settlement,
                                                take_profit=take_profit,
                                                stop_loss=stop_loss,
                                                status=status)
        result = con.execute(clause)
    except Exception:
        print('Got error Long')


def enter_positions(id_position, coin, size, date_ask, tick):
    orders_book.create_order()
    insert_long(id_position, coin, size, date_ask, tick, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                float(tick)+0.001, float(tick)*(1+0.05), float(tick)*(1-0.01), 'active')


def close_positions(id_position, coin):
    try:
        clause = long_positions.update(). \
            where(and_(long_positions.c.id_position == id_position, long_positions.c.coin == coin)). \
            values(status='closed')
        result = con.execute(clause)
    except Exception:
        print('Got error Close')


def exit_positions(exits):
    for e in exits:
        date_ask = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ordered = orders_book.create_order()
        ordered = dict({'date_settlement': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'settlement': (e.get('exit_price') - 0.001)})

        long_id = get_longs(e.get('coin'), e.get('id')).iloc[0]
        print(ordered.get('settlement') - long_id.settlement)
        close_positions(e.get('id'), e.get('coin'))
        shortPositions.insert_short(e.get('id'), e.get('coin'), e.get('size'), date_ask, e.get('exit_price'),
                                    ordered.get('date_settlement'), ordered.get('settlement'), e.get('source'))


def update_take_profit():
    # update open positions
    pass


def update_stop_loss():
    # update open positions
    pass
