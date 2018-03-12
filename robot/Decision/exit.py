import numpy as np
from datetime import datetime, timedelta
from robot.Extractor import signals, boillingers, tickers
from robot.Decision import exit


def set_take_profit():
    return 0.15


def set_stop_loss(coin, date):
    ticker_df = tickers.get_all_tickers_screen(coin, 0)[::-1]
    date_now = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    last_date_now = date_now - timedelta(hours=8)
    if len(ticker_df):
        _between = ticker_df[(ticker_df['date'] >= last_date_now) & (ticker_df['date'] <= date_now)]
        _between_sorted = _between.sort_values(by=['price'])
        stop_loss = min(_between_sorted.iloc[0].price, (1 - 0.05) * _between.iloc[0].price)
    return stop_loss


def strategy_one(tick, date, coin, open_positions):
    exits = []
    for index, row in open_positions.iterrows():
        take_profit = row.take_profit
        stop_loss = row.stop_loss
        if float(tick) >= take_profit:
            exits.append({'id': row.id_position,
                          'coin': coin,
                          'source': "take_profit",
                          'exit_price': float(tick),
                          'ask_date': date,
                          'size_position': row.size_position
                          })
            signals.insert_signal(date, coin, tick, 'SELL', 'EXIT_ONE')
        elif float(tick) <= stop_loss:
            exits.append({'id': row.id_position, 'coin': coin, 'source': "stop_loss", 'exit_price': float(tick),
                          'ask_date': date, 'size_position': row.size_position})
            signals.insert_signal(date, coin, tick, 'SELL', 'EXIT_ONE')
    return exits


def get_exit_channel(coin, date, tick, screen):
    boillingers_df = boillingers.get_boillinger(1, coin, date, screen)
    if boillingers_df.empty:
        return {'take_profit': 0,
                'stop_loss': 0}
    log_return_band = np.log(boillingers_df.iloc[0].upper_band/tick)
    return {'take_profit': (min(set_take_profit(), log_return_band) + 1) * tick,
            'stop_loss':  exit.set_stop_loss(coin, date)}
