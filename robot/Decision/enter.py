from robot.Decision import exit
from robot.Extractor import signals, emas, tickers, market_trend
from robot.Indicators import Ingestion


def strategy_one(coin, date, tick):
    entry_sign = Ingestion.get_ema_vote(date, coin, 1)
    trend_screen_one = market_trend.trend_market(date, coin)
    # trend_screen_two = trend_market(date, coin, 2)
    if trend_screen_one == 1 and entry_sign == 1:
        signals.insert_signal(date, coin, tick, 'BUY', 'ENTER_ONE')
        return {'signal': 'BUY',
                'take_profit': tick * (1 + 0.2),
                'stop_loss': tick * (1 - 0.1)}
    # elif vote_screen_one == -1 and vote_screen_two == -1 and entry_sign == -1:
    #     signals.insert_signal(date, coin, tick, 'SELL', 'ENTER_ONE')
    #     return {'signal': 'SELL',
    #             'take_profit': tick * (1 - 0.15),
    #             'stop_loss': tick * (1 - 0.05)}
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_ONE')
        return None


def channel_strategy(coin, date, tick):
    ema = emas.get_emas(1, coin, date, 1)
    if not ema.empty:
        exit_points = exit.get_exit_channel(coin, date, tick, 1)
        if ema.iloc[0].ema20 > ticks.iloc[0].price > ema.iloc[0].ema20 * (1 - 0.05) and ema.iloc[0].ema20 > ticks.iloc[
            1].price and trend_screen_one == 1:
            signals.insert_signal(date, coin, tick, 'BUY', 'ENTER_TWO')
            return {'signal': 'BUY',
                    'take_profit': exit_points.get('take_profit'),
                    'stop_loss': exit_points.get('stop_loss')}
        # elif ema.iloc[0].ema20 < tick < ema.iloc[0].ema20 * (1 + 0.1) and trend_two == -1 and trend_one == -1:
        #     signals.insert_signal(date, coin, tick, 'SELL', 'ENTER_TWO')
        #     return {'signal': 'SELL',
        #             'take_profit': exit_points.get('take_profit'),
        #             'stop_loss': exit_points.get('stop_loss')}
        else:
            signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
            return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
        return None


def strategy_two(coin, date, tick):
    trend_screen_one = market_trend.trend_market(date, coin)
    ticks = tickers.get_tickers(2, coin, date, 0)
    # trend_screen_two = trend_market(date, coin, 2)
    ema = emas.get_emas(1, coin, date, 1)
    if not ema.empty:
        exit_points = exit.get_exit_channel(coin, date, tick, 1)
        if ema.iloc[0].ema5 > ticks.iloc[0].price > ema.iloc[0].ema5 * (1 - 0.05) and ema.iloc[0].ema5 > ticks.iloc[1].price and trend_screen_one == 1:
            signals.insert_signal(date, coin, tick, 'BUY', 'ENTER_TWO')
            return {'signal': 'BUY',
                    'take_profit': exit_points.get('take_profit'),
                    'stop_loss': exit_points.get('stop_loss')}
        # elif ema.iloc[0].ema20 < tick < ema.iloc[0].ema20 * (1 + 0.1) and trend_two == -1 and trend_one == -1:
        #     signals.insert_signal(date, coin, tick, 'SELL', 'ENTER_TWO')
        #     return {'signal': 'SELL',
        #             'take_profit': exit_points.get('take_profit'),
        #             'stop_loss': exit_points.get('stop_loss')}
        else:
            signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
            return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT', 'ENTER_TWO')
        return None
