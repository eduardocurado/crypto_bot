from datetime import datetime

from robot.Binance import services
from robot.Decision import features
from robot.Extractor import votes
from robot.Indicators import Calculator, Assessment


def update_indicators(date, coin, screen):
    Calculator.calculate_sma(date, coin, screen)
    Calculator.calculate_ema(date, coin, screen)
    Calculator.calculate_rsi(date, coin, screen)
    Calculator.calculate_macd(date, coin, screen)
    Calculator.calculate_boillinger(date, coin, screen)


def update_votes(date, coin):
    vote_sma = Assessment.get_sma_vote(date, coin)
    vote_ema = Assessment.get_ema_vote(date, coin)
    vote_rsi = Assessment.get_rsi_vote(date, coin)
    vote_boillinger = Assessment.get_boillinger_vote(date, coin)
    vote_macd = Assessment.get_macd_vote(date, coin)
    votes.insert_votes(date, coin, vote_sma, vote_ema, vote_rsi, vote_boillinger, vote_macd)


def update_screen(interval, coin, screen):
    services.triple_screen(interval, coin, screen)
    features.update_indicators(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, screen)
