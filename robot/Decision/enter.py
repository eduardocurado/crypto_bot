import numpy as np

from robot.Decision import exit
from robot.Extractor import signals, emas, tickers, market_trend, rsis, macds
from robot.Indicators import Ingestion


def cross_over_strategy(coin, date, tick):
    trend_screen_one = market_trend.trend_market(date, coin)
    entry_sign = 0
    ema_df = emas.get_emas(2, coin, date, 2)
    if len(ema_df) < 2:
        signals.insert_signal(date, coin, tick, 'OUT', 'CROSS_OVER')
        return None
    ema5_prev = ema_df.iloc[0].ema5
    ema20_prev = ema_df.iloc[0].ema20
    ema5 = ema_df.iloc[1].ema5
    ema20 = ema_df.iloc[1].ema20

    if ema5_prev > ema20_prev:
        versus_ema_prev = 1
    else:
        versus_ema_prev = -1
    if ema5 > ema20:
        versus_ema = 1
    else:
        versus_ema = -1

    if versus_ema_prev == -1 and versus_ema == 1:
        entry_sign = 1
    if versus_ema_prev == 1 and versus_ema == -1:
        entry_sign = -1

    if trend_screen_one == 1 and entry_sign == 1:
        signals.insert_signal(date, coin, tick, 'BUY', 'CROSS_OVER')
        return {'signal': 'BUY',
                'take_profit': tick * (1 + exit.set_take_profit()),
                'stop_loss': exit.set_stop_loss(coin, date)}
    elif trend_screen_one == -1 and entry_sign == -1:
        signals.insert_signal(date, coin, tick, 'SELL', 'CROSS_OVER')
        return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'CROSS_OVER')
        return None


def rsi_strategy(coin, date, tick):
    n = 3
    rsi_df = rsis.get_rsis(n, coin, date, 1)

    if len(rsi_df) < n:
        signals.insert_signal(date, coin, tick, 'OUT', 'RSI')
        return None

    rsi_value = rsi_df.iloc[0].rsi
    rsi_value_last = rsi_df.iloc[(n-1)].rsi

    if rsi_value < 20 < rsi_value_last:
        signals.insert_signal(date, coin, tick, 'BUY', 'RSI')
        return {'signal': 'BUY',
                'take_profit': tick * (1 + exit.set_take_profit()),
                'stop_loss': exit.set_stop_loss(coin, date)}
    elif rsi_value > 80 > rsi_value_last:
        signals.insert_signal(date, coin, tick, 'SELL', 'RSI')
        return {'signal': 'SELL',
                'take_profit': tick * (1 - exit.set_take_profit()),
                'stop_loss': exit.set_stop_loss(coin, date)}

    signals.insert_signal(date, coin, tick, 'OUT', 'RSI')
    return None


def channel_strategy(coin, date, tick):
    # trend_screen_one = market_trend.trend_market(date, coin)
    ticks = tickers.get_tickers(2, coin, date, 0)
    # trend_screen_two = trend_market(date, coin, 2)
    macd_df = macds.get_macds(1, coin, date, 1)
    # ema = emas.get_emas(1, coin, date, 1)

    if not macd_df.empty:
        exit_points = exit.get_exit_channel(coin, date, tick, 1)
        dif_ema = np.log(ticks.iloc[0].price/macd_df.iloc[0].ema12)
        trend_screen_one = market_trend.trend_market(date, coin, ticks.iloc[0].price, dif_ema)
        if trend_screen_one == 1:
            return {'signal': 'BUY',
                        'take_profit': exit_points.get('take_profit'),
                        'stop_loss': exit_points.get('stop_loss')}
        # if - 0.1 < dif_ema < 1 == trend_screen_one:
        #     signals.insert_signal(date, coin, tick, 'BUY', 'CHANNEL')
        #     return {'signal': 'BUY',
        #             'take_profit': exit_points.get('take_profit'),
        #             'stop_loss': exit_points.get('stop_loss')}
        #
        # elif macd_df.iloc[0].ema12 < ticks.iloc[0].price < macd_df.iloc[0].ema12 * (1 + 0.1) and trend_screen_one == -1:
        #     signals.insert_signal(date, coin, tick, 'SELL', 'CHANNEL')
        #     return None
        #
        # else:
        #     signals.insert_signal(date, coin, tick, 'OUT', 'CHANNEL')
        #     return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'CHANNEL')
