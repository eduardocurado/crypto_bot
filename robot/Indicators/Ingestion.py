from robot.Extractor import tickers, smas, rsis, emas, boillingers, macds


def get_sma_vote(date, coin, screen):
    vote = 0
    sma_df = smas.get_smas(2, coin, date, screen)
    if len(sma_df) == 2:
        sma5_prev = sma_df.iloc[0].sma5
        sma20_prev = sma_df.iloc[0].sma20
        sma5 = sma_df.iloc[1].sma5
        sma20 = sma_df.iloc[1].sma20
        # SMA CROSSOVER
        if sma5_prev >= sma20_prev:
            versus_sma_prev = 1
        else:
            versus_sma_prev = 0
        if sma5 >= sma20:
            versus_sma = 1
        else:
            versus_sma = 0
        if (versus_sma_prev == 0) & (versus_sma == 1):
            vote = 1

        if (versus_sma_prev == 1) & (versus_sma == 0):
            vote = -1
    return vote


def get_ema_vote(date, coin, screen):
    vote = 0
    ema_df = emas.get_emas(2, coin, date, screen)
    if len(ema_df) == 2:
        ema5_prev = ema_df.iloc[0].ema5
        ema20_prev = ema_df.iloc[0].ema20
        ema5 = ema_df.iloc[1].ema5
        ema20 = ema_df.iloc[1].ema20
        # ema CROSSOVER
        if ema5_prev >= ema20_prev:
            versus_ema_prev = 1
        else:
            versus_ema_prev = 0
        if ema5 >= ema20:
            versus_ema = 1
        else:
            versus_ema = 0
        if (versus_ema_prev == 0) & (versus_ema == 1):
            vote = 1

        if (versus_ema_prev == 1) & (versus_ema == 0):
            vote = -1
    return vote


def get_rsi_vote(date, coin, screen):
    # RSI
    vote = 0
    rsi_df = rsis.get_rsis(1, coin, date, screen)
    if not rsi_df.empty:
        if len(rsi_df) == 1:
            rsi_value = rsi_df.iloc[0].rsi
            if rsi_value < 30:
                vote = 1
            if rsi_value > 70:
                vote = -1

    return vote


def get_boillinger_vote(date, coin, screen):
    vote = 0
    boillinger_df = boillingers.get_boillinger(1, coin, date, screen)
    if not boillinger_df.empty:
        tickers_df = tickers.get_tickers(1, coin, date)
        if not tickers_df.empty:
            price = tickers_df.iloc[0].price
            lower_band = boillinger_df.iloc[0].lower_band
            upper_band = boillinger_df.iloc[0].upper_band
            if price < lower_band:
                vote = 1
            elif price > upper_band:
                vote = -1
    return vote


def get_macd_vote(date, coin, screen):
    vote = 0
    macd_df = macds.get_macds(2, coin, date, screen)
    if len(macd_df) == 2:
        macd_line_prev = macd_df.iloc[0].macd_line
        signal_line_prev = macd_df.iloc[0].signal_line
        macd_line = macd_df.iloc[1].macd_line
        signal_line = macd_df.iloc[1].signal_line
        histogram = macd_df.iloc[1].histogram
        # MACD
        if macd_line_prev >= signal_line_prev:
            versus_macd_prev = 1
        else:
            versus_macd_prev = 0

        if macd_line >= signal_line:
            versus_macd = 1
        else:
            versus_macd = 0

        if (versus_macd_prev == 0) & (versus_macd == 1) | (versus_macd_prev == 1) & (versus_macd == 0):
            if histogram >= 0:
                vote = 1
            else:
                vote = -1
        else:
            if histogram >= 0:
                vote = 0
            else:
                vote = 0
    return vote


def trend_market(date, coin, screen):
    ema_df = emas.get_emas(10, coin, date, screen)
    print(ema_df)
    if len(ema_df) < 3:
        return {'long_vote': 0, 'short_vote': 0}
    base_ema20 = ema_df.iloc[len(ema_df) - 1].ema20
    current_ema20 = ema_df.iloc[0].ema20
    base_ema5 = ema_df.iloc[len(ema_df)-1].ema5
    current_ema5 = ema_df.iloc[0].ema5
    vote_long = 0
    vote_short = 0
    if current_ema20 and base_ema20:
        if current_ema20 - base_ema20 > 0:
            vote_long = 1
        elif current_ema20 - base_ema20 < 0:
            vote_long = -1
        else:
            vote_long = 0
    if current_ema5 and base_ema5:
        if current_ema5 - base_ema5 > 0:
            vote_short = 1
        elif current_ema5 - base_ema5 < 0:
            vote_short = -1
        else:
            vote_short = 0
    return {'long_vote': vote_long, 'short_vote': vote_short}
