import pandas as pd
from sqlalchemy.sql import select, and_, or_, not_, desc, asc
from sqlalchemy import Table, Column, Integer, Date, DateTime, String,Float, ForeignKey
from robot.Utils import Initializations


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
votes = Table('Vote', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('sma', Integer),
    Column('ema', Integer),
    Column('rsi', Integer),
    Column('boillinger', Integer),
    Column('macd', Integer),
    Column('screen', Integer, primary_key=True)
)


def insert_votes(date, coin, vote_sma, vote_ema, vote_rsi, vote_boillinger, vote_macd, screen):
    try:
        clause = votes.insert().values(date=date, coin=coin, sma=vote_sma, ema=vote_ema,
                                       rsi=vote_rsi, boillinger=vote_boillinger, macd=vote_macd, screen=screen)
        con.execute(clause)
    except Exception:
        print("Got error Votes! " + repr(Exception))


def get_votes(n, coin, date, screen):
    s = select([votes])\
        .where(and_(votes.c.coin == coin, votes.c.date <= date, votes.c.screen == screen))\
        .order_by(
        desc(votes.c.date)).limit(n)
    rows = con.execute(s)
    votes_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not votes_df.empty:
        votes_df.columns = rows.keys()
    return votes_df
