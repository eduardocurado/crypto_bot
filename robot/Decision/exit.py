import numpy as np
from robot.Extractor import signals, boillingers


def set_take_profit():
    return 0.20


def set_stop_loss():
    return 0.05


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
            'stop_loss': tick * (1 - set_stop_loss())}
