from robot.Extractor import votes
from robot.Indicators import Ingestion
from robot.Extractor import signals


def strategy_one(coin, date, tick):
    vote_screen_one = Ingestion.get_ema_vote(date, coin, 1)
    print(vote_screen_one)
    vote_screen_two = Ingestion.trend_market(date, coin, 2)['long_vote']
    print(vote_screen_two)
    if vote_screen_one == 1 or vote_screen_two == 1:
        signals.insert_signal(date, coin, tick, 'BUY')
        return "BUY"
    elif vote_screen_one == -1 or vote_screen_two == -1:
        signals.insert_signal(date, coin, tick, 'SELL')
        return "SELL"
    else:
        signals.insert_signal(date, coin, tick, 'OUT')
        return "OUT"
