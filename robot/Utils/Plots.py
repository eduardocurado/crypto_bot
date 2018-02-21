import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime
from sqlalchemy.sql import select, and_, or_, not_, desc, asc


def plot_screen(coin, n, date=datetime.today().strftime('%Y-%m-%d')):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    s = select([tickers]).where(and_(tickers.c.coin == coin, tickers.c.date <= date)).order_by(
        desc(tickers.c.date)).limit(n)
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    tickers_df.columns = rows.keys()

    s = select([ema]).where(and_(ema.c.coin == coin, ema.c.date <= date)).order_by(desc(ema.c.date)).limit(n)
    rows = con.execute(s)
    ema_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    ema_df.columns = rows.keys()

    fig, ax = plt.subplots()
    # format the ticks
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.plot(tickers_df.date.values, tickers_df.price.values)
    ax.plot(ema_df.date.values, ema_df.ema5.values)
    ax.plot(ema_df.date.values, ema_df.ema20.values)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #     ax.set_ylim(0, 25000)
    fig.autofmt_xdate()
    plt.show()


def plot_screen_2(coin, n, date=datetime.today().strftime('%Y-%m-%d')):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    s = select([macd]).where(and_(macd.c.coin == coin, macd.c.date <= date)).order_by(desc(macd.c.date)).limit(n)
    rows = con.execute(s)
    macd_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    macd_df.columns = rows.keys()

    fig, ax = plt.subplots()
    # format the ticks
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.plot(macd_df.date.values, macd_df.macd_line.values)
    ax.plot(macd_df.date.values, macd_df.signal_line.values)
    ax.bar(macd_df.date.values, macd_df.histogram.values)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #     ax.set_ylim(0, 25000)
    fig.autofmt_xdate()
    plt.show()


def plot_screen_3(coin, n, date=datetime.today().strftime('%Y-%m-%d')):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    s = select([tickers]).where(and_(tickers.c.coin == coin, tickers.c.date <= date)).order_by(
        desc(tickers.c.date)).limit(n)
    rows = con.execute(s)
    tickers_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    tickers_df.columns = rows.keys()

    s = select([boillinger]).where(and_(boillinger.c.coin == coin, boillinger.c.date <= date)).order_by(
        desc(boillinger.c.date)).limit(n)
    rows = con.execute(s)
    boillinger_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    boillinger_df.columns = rows.keys()

    s = select([ema]).where(and_(ema.c.coin == coin, ema.c.date <= date)).order_by(desc(ema.c.date)).limit(n)
    rows = con.execute(s)
    ema_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    ema_df.columns = rows.keys()
    fig, ax = plt.subplots()
    # format the ticks
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.plot(tickers_df.date.values, tickers_df.price.values)
    ax.plot(boillinger_df.date.values, boillinger_df.upper_band.values)
    ax.plot(boillinger_df.date.values, boillinger_df.lower_band.values)
    ax.plot(ema_df.date.values, ema_df.ema20.values)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #     ax.set_ylim(0, 25000)
    fig.autofmt_xdate()
    plt.show()


def plot_screen_4(coin, n, date=datetime.today().strftime('%Y-%m-%d')):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    s = select([rsi]).where(and_(rsi.c.coin == coin, rsi.c.date <= date)).order_by(desc(rsi.c.date)).limit(n)
    rows = con.execute(s)
    rsi_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    rsi_df.columns = rows.keys()

    fig, ax = plt.subplots()
    # format the ticks
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.plot(rsi_df.date.values, rsi_df.rsi.values)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_ylim(0, 100)
    plt.axhline(y=75, color='k')
    plt.axhline(y=25, color='k')
    fig.autofmt_xdate()
    plt.show()


def plot_screen_5(coin, n, date=datetime.today().strftime('%Y-%m-%d')):
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    s = select([sma]).where(and_(sma.c.coin == coin, sma.c.date <= date)).order_by(desc(sma.c.date)).limit(n)
    rows = con.execute(s)
    sma_df = pd.DataFrame(rows.fetchall()).iloc[::-1]
    sma_df.columns = rows.keys()
    #     print(sma_df.describe())
    fig, ax = plt.subplots()
    # format the ticks
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    #     ax.scatter(sma_df.date.values, sma_df.sma5_theta.values)
    ax.hist(sma_df.sma5_theta.values, bins=30, range=[-95, -85])
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #     ax.set_xlim(-0.75, -0.9)
    fig.autofmt_xdate()
    plt.show()
