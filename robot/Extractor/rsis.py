import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import quandl
import pickle
from datetime import datetime, timedelta
import re
import psycopg2
import sys
import sqlalchemy
from sqlalchemy.sql import select, and_, or_, not_, desc, asc
from sqlalchemy import Table, Column, Integer, Date, DateTime, String,Float, ForeignKey
from sqlalchemy.orm import sessionmaker
from robot.Indicators import Calculator, Ingestion
from robot.Utils import Initializations, Plots


con, meta = Initializations.connect_db('postgres', '', 'robotdb')
rsi = Table('Rsi', meta,
    Column('date', DateTime, primary_key = True),
    Column('coin', String, primary_key = True),
    Column('rsi', Float),
    Column('screen', Integer, primary_key=True)
)


def get_rsis(n, coin, date, screen):
    con, meta = Initializations.connect_db('postgres', '', 'robotdb')
    s = select([rsi])\
        .where(and_(rsi.c.coin == coin, rsi.c.date <= date, rsi.c.screen == screen))\
        .order_by(
        desc(rsi.c.date)).limit(n)
    rows = con.execute(s)
    rsi_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    if not rsi_df.empty:
        rsi_df.columns = rows.keys()
    return rsi_df


def insert_rsi(date, coin, rsi_value, screen):
    try:
        clause = rsi.insert().values(date=date, coin=coin, rsi=rsi_value, screen=screen)
        result = con.execute(clause)
        #                 print('Done.')
    except Exception:
        return
        #print("Got error! RSI" + repr(Exception))
        #     print('Nothing Inserted')
