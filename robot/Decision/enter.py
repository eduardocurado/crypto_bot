from robot.Indicators import Ingestion
from robot.Extractor import signals, emas
from robot.Decision import exit


def strategy_one(coin, date, tick):
    vote_screen_one = Ingestion.get_ema_vote(date, coin, 1)
    vote_screen_two = Ingestion.trend_market(date, coin, 2)['long_vote']
    if vote_screen_one == 1 and vote_screen_two == 1:
        signals.insert_signal(date, coin, tick, 'BUY')
        return {'signal': 'BUY',
                'take_profit': tick * (1 + 0.2),
                'stop_loss': tick * (1 - 0.1)}
    elif vote_screen_one == -1 and vote_screen_two == -1:
        signals.insert_signal(date, coin, tick, 'SELL')
        return {'signal': 'SELL',
                'take_profit': tick * (1 - 0.15),
                'stop_loss': tick * (1 + 0.1)}
    else:
        signals.insert_signal(date, coin, tick, 'OUT')
        return None


def strategy_two(coin, date, tick):
    trend_one = Ingestion.trend_market(date, coin, 1)['long_vote']
    trend_two = Ingestion.trend_market(date, coin, 2)['long_vote']
    ema = emas.get_emas(1, coin, date, 1)
    if not ema.empty:
        exit_points = exit.get_exit_channel(coin, date, tick, 1)
        if ema.iloc[0].ema20 < tick < ema.iloc[0].ema20 * (1 + 0.1) and trend_two == -1 and trend_one == -1:
            signals.insert_signal(date, coin, tick, 'SELL')
            return {'signal': 'SELL',
                    'take_profit': exit_points.get('take_profit'),
                    'stop_loss': exit_points.get('stop_loss')}
        elif ema.iloc[0].ema20 > tick > ema.iloc[0].ema20 * (1 - 0.1) and trend_two == 1 and trend_one == 1:
            signals.insert_signal(date, coin, tick, 'BUY')
            return {'signal': 'BUY',
                    'take_profit': exit_points.get('take_profit'),
                    'stop_loss': exit_points.get('stop_loss')}
        else:
            signals.insert_signal(date, coin, tick, 'OUT')
            return None
    else:
        signals.insert_signal(date, coin, tick, 'OUT')
        return None
