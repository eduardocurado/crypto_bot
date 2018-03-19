from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy import Table, Column, Integer, DateTime, String, Float
from robot.Poloniex import feeder


def connect_db(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    url = 'postgresql+psycopg2://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con)
    return con, meta


def drop_all_tables(user, password, db, host='localhost', port=5432):
    url = 'postgresql+psycopg2://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con)
    meta.reflect()
    result = meta.drop_all()
    return con, meta


def create_all_tables(user, password, db, host='localhost', port=5432):
    con, meta = connect_db('postgres', '', 'robotdb')
    tickers = Table('Ticker', meta,
                    Column('date', DateTime, primary_key=True),
                    Column('coin', String, primary_key=True),
                    Column('price', Float),
                    Column('volume', Float),
                    Column('screen', Integer, primary_key=True)
                    )

    sma = Table('Sma', meta,
                Column('date', DateTime, primary_key=True),
                Column('coin', String, primary_key=True),
                Column('sma5', Float),
                Column('sma20', Float),
                Column('sma5_theta', Float),
                Column('sma20_theta', Float),
                Column('screen', Integer, primary_key=True)
                )

    ema = Table('Ema', meta,
                Column('date', DateTime, primary_key=True),
                Column('coin', String, primary_key=True),
                Column('ema5', Float),
                Column('ema20', Float),
                Column('ema5_theta', Float),
                Column('ema20_theta', Float),
                Column('screen', Integer, primary_key=True)
                )

    rsi = Table('Rsi', meta,
                Column('date', DateTime, primary_key=True),
                Column('coin', String, primary_key=True),
                Column('rsi', Float),
                Column('screen', Integer, primary_key=True)
                )

    boillinger = Table('Boillinger', meta,
                       Column('date', DateTime, primary_key=True),
                       Column('coin', String, primary_key=True),
                       Column('upper_band', Float),
                       Column('lower_band', Float),
                       Column('sma20', Float),
                       Column('height', Float),
                       Column('screen', Integer, primary_key=True)
                       )

    macd = Table('Macd', meta,
                 Column('date', DateTime, primary_key=True),
                 Column('coin', String, primary_key=True),
                 Column('ema12', Float),
                 Column('ema_26', Float),
                 Column('macd_line', Float),
                 Column('signal_line', Float),
                 Column('histogram', Float),
                 Column('screen', Integer, primary_key=True)
                 )

    votes = Table('Vote', meta,
                  Column('date', DateTime, primary_key=True),
                  Column('coin', String, primary_key=True),
                  Column('sma', Integer),
                  Column('ema', Integer),
                  Column('rsi', Integer),
                  Column('boillinger', Integer),
                  Column('macd', Integer),
                  Column('screen', Integer, primary_key=True)
                  )

    long_positions = Table('Long', meta,
                           Column('id_position', Integer, primary_key=True),
                           Column('coin', String, primary_key=True),
                           Column('strategy', String),
                           Column('size_position', Float),
                           Column('date_ask', DateTime),
                           Column('ask', Float),
                           Column('date_settlement', DateTime),
                           Column('settlement', Float),
                           Column('take_profit', Float),
                           Column('stop_loss', Float),
                           Column('exit_date', DateTime),
                           Column('exit_price', Float),
                           Column('log_return', Float),
                           Column('status', String),
                           Column('source', String)
                           )

    short_positions = Table('Short', meta,
                            Column('id_position', Integer, primary_key=True),
                            Column('coin', String, primary_key=True),
                            Column('size_position', Float),
                            Column('date_ask', DateTime),
                            Column('ask', Float),
                            Column('date_settlement', DateTime),
                            Column('settlement', Float),
                            Column('source', String)
                            )

    signal = Table('Signal', meta,
                   Column('date', DateTime, primary_key=True),
                   Column('coin', String, primary_key=True),
                   Column('tick', Float),
                   Column('signal', String, primary_key=True),
                   Column('signal_source', String, primary_key=True)
                   )

    mkt_trend = Table('Market_trend', meta,
                      Column('coin', String, primary_key=True),
                      Column('date', DateTime, primary_key=True),
                      Column('screen', Integer, primary_key=True),
                      Column('dif_current', Float),
                      Column('dif_base', Float),
                      Column('d_dif', Float),
                      Column('theta_current', Float),
                      Column('theta_base', Float),
                      Column('d_theta', Float),
                      Column('max_growth', Float),
                      Column('vote', Integer)
                      )

    balances = Table('Balance', meta,
                     Column('date', DateTime, primary_key=True),
                     Column('coin', String, primary_key=True),
                     Column('size_position', Float)
                     )

    return con, meta


def restore_backup(days):
    from pathlib import Path
    import os
    path_dir = 'Dumps/'
    file_path = Path(path_dir + 'dump_' + str(days) + '.backup')
    if file_path.exists():
        os.system('psql -U postgres -d robotdb < Dumps/dump_' + str(days) + '.backup >/dev/null 2>&1')
        print('Restoring DB ...')
        return True
    else:
        return False


def create_backup(days):
    import os
    os.system('pg_dump -U postgres robotdb -f Dumps/dump_' + str(days) + '.backup')
    print("backup_successfull")


def feed_historical_data(coin, days):
    start = (datetime.now() - timedelta(days=days)).timestamp()
    print('Feeding base data')
    size_historical = feeder.get_historical_data(coin, start)
    print('Feeding screen 1')
    feeder.get_historical_screen(4, coin, 1)
    print('Feeding screen 2')
    feeder.get_historical_screen(24, coin, 2)

    return size_historical


def set_up_bd(days):
    drop_all_tables('postgres', '', 'robotdb')
    restored = restore_backup(days)
    if restored:
        create_all_tables('postgres', '', 'robotdb')
        return True
    con, meta = create_all_tables('postgres', '', 'robotdb')
    meta.create_all(con)
    return False
