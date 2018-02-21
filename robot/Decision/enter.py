from robot.Extractor import votes


def strategy_one():
    return 1
    # votes_df = votes.get_votes(1, coin, date).iloc[0]
    # votes_sum = votes_df.sma + votes_df.rsi + votes_df.ema + votes_df.macd + votes_df.boillinger
    # if votes_sum > 1:
    #     return "BUY"
    # elif votes_sum < -1:
    #     return "SELL"
    # else:
    #     return "STAY OUT"
