import quandl
import pickle
import sqlalchemy
from sqlalchemy import Table, Column, Integer, DateTime, String, Float


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
                           Column('size', Float),
                           Column('date_ask', DateTime),
                           Column('ask', Float),
                           Column('date_settlement', DateTime),
                           Column('settlement', Float),
                           Column('take_profit', Float),
                           Column('stop_loss', Float),
                           Column('status', String)
                           )
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

    meta.create_all(con)
    return con, meta


def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = '{}.pkl'.format(quandl_id).replace('/', '-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df
