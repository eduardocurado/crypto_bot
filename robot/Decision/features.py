from datetime import datetime

from robot.Decision import features
from robot.Extractor import votes
from robot.Indicators import Calculator, Ingestion
from robot.Utils import services


def update_indicators(date, coin, screen):
    Calculator.calculate_sma(date, coin, screen)
    Calculator.calculate_ema(date, coin, screen)
    Calculator.calculate_rsi(date, coin, screen)
    Calculator.calculate_macd(date, coin, screen)
    Calculator.calculate_boillinger(date, coin, screen)


def update_votes(date, coin):
    vote_sma = Ingestion.get_sma_vote(date, coin)
    vote_ema = Ingestion.get_ema_vote(date, coin)
    vote_rsi = Ingestion.get_rsi_vote(date, coin)
    vote_boillinger = Ingestion.get_boillinger_vote(date, coin)
    vote_macd = Ingestion.get_macd_vote(date, coin)
    votes.insert_votes(date, coin, vote_sma, vote_ema, vote_rsi, vote_boillinger, vote_macd)


def update_screen(interval, coin, screen):
    services.triple_screen(interval, coin, screen)
    features.update_indicators(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, screen)


def update_position():
    pass


def update_balance():
    pass

