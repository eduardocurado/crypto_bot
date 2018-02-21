from datetime import datetime
import time
from robot.Poloniex import extractor
from robot.Utils import Initializations
from robot.Decision import features, exit, enter
from robot.Extractor import longPositions


def main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    coin = 'BTC_ETH'
    Initializations.drop_all_tables('postgres', '', 'robotdb')
    Initializations.create_all_tables('postgres', '', 'robotdb')
    size_historical = extractor.get_historical_data('BTC_ETH')
    extractor.get_historical_screen(size_historical, 4, 'BTC_ETH', 1)
    extractor.get_historical_screen(size_historical, 24, 'BTC_ETH', 2)
    start = datetime.now()
    last_date = start
    while 1:
        print(last_date)
        time.sleep(TIME_DEFAULT)
        tick, last_date = extractor.get_tick(coin)
        if not tick:
            print("ERROR")
            continue
        print(tick)
        exits = exit.strategy_one(tick, coin)
        if exits:
            print(exits)
        # do_exit()
        longPositions.exit_positions(exits)
        features.update_indicators(last_date, coin, 0)
        TIME_DEFAULT_COUNT += 1
        if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL or not TIME_DEFAULT_COUNT % LONG_INTERVAL:
            if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL:
                features.update_screen(INTERMEDIATE_INTERVAL, coin, 1)
            if not TIME_DEFAULT_COUNT % LONG_INTERVAL:
                features.update_screen(LONG_INTERVAL, coin, 2)
            entry_sign = enter.strategy_one()
            if entry_sign:
                longPositions.enter_positions(TIME_DEFAULT_COUNT, coin, last_date, tick)




TIME_DEFAULT = 1
INTERMEDIATE_INTERVAL = 5*TIME_DEFAULT  # S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL)