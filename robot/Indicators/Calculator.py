import numpy as np
from robot.Extractor import tickers, smas, rsis, emas, boillingers, macds


def calculate_theta(date, coin, actual, screen):
    import math
    sma_df = smas.get_smas(5, coin, date, screen)
    if len(sma_df) < 5:
        return 0
    deltax = 5
    deltay = actual - sma_df.iloc[0].sma5
    return math.degrees(np.arctan(deltay / deltax))


def calculate_sma(date, coin, screen):
    tickers_df = tickers.get_tickers(20, coin, date, screen)
    if len(tickers_df) >= 5:
        sma5 = tickers_df.iloc[(len(tickers_df) - 5):len(tickers_df)].price.mean()
        sma5_theta = calculate_theta(date, coin, sma5, screen)
        if len(tickers_df) >= 20:
            sma20 = tickers_df.iloc[(len(tickers_df) - 20):len(tickers_df)].price.mean()
            smas.insert_smas(date, coin, sma5, sma20, sma5_theta, screen)


def calculate_ema(date, coin, screen):
    tickers_df = tickers.get_tickers(20, coin, date, screen)
    if len(tickers_df) >= 5:
        ema5 = tickers_df.iloc[(len(tickers_df) - 5):len(tickers_df)].price.ewm(span=5, min_periods=5, adjust=True,
                                                                                ignore_na=False).mean()
        ema5 = ema5.iloc[4]
        if len(tickers_df) >= 20:
            ema20 = tickers_df.iloc[(len(tickers_df) - 20):len(tickers_df)].price.ewm(span=20, min_periods=20,
                                                                                      adjust=True,
                                                                                      ignore_na=False).mean()
            ema20 = ema20.iloc[19]
            emas.insert_emas(date, coin, ema5, ema20, screen)


def calculate_rsi(date, coin, screen):
    tickers_df = tickers.get_tickers(15, coin, date, screen)
    if len(tickers_df) >= 15:
        profit = []
        loss = []
        df = tickers_df.iloc[(len(tickers_df) - 15):len(tickers_df)]
        for i in range(len(df)):
            if i == 0:
                continue
            last_d = df.price.values[i]
            last_d1 = df.price.values[(i - 1)]
            dif = last_d - last_d1
            if dif >= 0:
                profit.append(dif)
            else:
                loss.append(dif * (-1))
        if len(profit) == 0:
            rs = 0
        else:
            if len(loss) == 0:
                rs = 100
            else:
                rs = np.mean(profit) / np.mean(loss)
        # RSI = 100 - 100 / (1 + RS)
        rsi_value = 100 - (100 / (1 + rs))
        rsis.insert_rsi(date, coin, rsi_value, screen)


def calculate_boillinger(date, coin, screen):
    tickers_df = tickers.get_tickers(20, coin, date, screen)
    if len(tickers_df) >= 20:
        sma20 = tickers_df.iloc[(len(tickers_df) - 20):len(tickers_df)].price.mean()
        std20 = tickers_df.iloc[(len(tickers_df) - 20):len(tickers_df)].price.std()
        ema20 = emas.get_emas(1, coin, date, screen).iloc[0].ema20
        # upper_band = sma20 + 2 * std20
        # lower_band = sma20 - 2 * std20]
        #TODO: CHANGE PERCENTAGE TO A LIL BIT BIGGER
        upper_band = ema20 * (1 + 0.15)
        lower_band = ema20 * (1 - 0.15)
        height = upper_band - lower_band
        boillingers.insert_boillingers(date, coin, upper_band, lower_band, ema20, height, screen)


def calculate_macd(date, coin, screen):
    signal_line = np.NaN
    histogram = np.NaN
    tickers_df = tickers.get_tickers(26, coin, date, screen)
    if len(tickers_df) >= 26:
        ema_12 = tickers_df.iloc[len(tickers_df) - 12: len(tickers_df)].drop(['date', 'coin'], axis=1).price.ewm(
            span=12, min_periods=12, adjust=True, ignore_na=False).mean()
        ema_26 = tickers_df.iloc[len(tickers_df) - 26: len(tickers_df)].drop(['date', 'coin'], axis=1).price.ewm(
            span=26, min_periods=26, adjust=True, ignore_na=False).mean()
        ema12 = ema_12.iloc[11]
        ema26 = ema_26.iloc[25]
        macd_line = ema_12 - ema_26
        macd_df = macds.get_macds(9, coin, date, screen)
        if len(macd_df) >= 9:
            signal_line = macd_df.iloc[len(macd_df) - 9: len(macd_df)].macd_line.ewm(span=9, min_periods=9,
                                                                                     adjust=True,
                                                                                     ignore_na=False).mean()
            signal_line = signal_line[0]
            histogram = macd_line[0] - signal_line
        macds.insert_macd(date, coin, ema12, ema26, macd_line[0], signal_line, histogram, screen)
