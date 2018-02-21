from datetime import datetime
import time
from robot.Poloniex import feeder
from robot.Utils import Initializations
from robot.Decision import features, exit, enter
from robot.Extractor import longPositions


def main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    coin = 'BTC_ETH'
    Initializations.drop_all_tables('postgres', '', 'robotdb')
    Initializations.create_all_tables('postgres', '', 'robotdb')
    size_historical = feeder.get_historical_data('BTC_ETH')
    feeder.get_historical_screen(size_historical, 4, 'BTC_ETH', 1)
    feeder.get_historical_screen(size_historical, 24, 'BTC_ETH', 2)

    #start_getting new data
    start = datetime.now()
    print(start)
    while 1:
        time.sleep(TIME_DEFAULT)
        tick, last_date = feeder.get_tick(coin)
        if not tick:
            print("ERROR")
            continue
        print(tick)
        open_positions = longPositions.get_open_positions(coin)
        exits = exit.strategy_one(tick, coin, open_positions)
        if exits:
            longPositions.exit_positions(exits)
            features.update_balance()
        #update_take_profit()
        #update_stop_loss()
        features.update_indicators(last_date, coin, 0)
        TIME_DEFAULT_COUNT += 1
        if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL or not TIME_DEFAULT_COUNT % LONG_INTERVAL:
            if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL:
                features.update_screen(INTERMEDIATE_INTERVAL, coin, 1)
            if not TIME_DEFAULT_COUNT % LONG_INTERVAL:
                features.update_screen(LONG_INTERVAL, coin, 2)

            entry_sign, size_operation = enter.strategy_one()
            if entry_sign:
                longPositions.enter_positions(TIME_DEFAULT_COUNT, coin, size_operation, last_date, tick)
                features.update_balance()




TIME_DEFAULT = 5
INTERMEDIATE_INTERVAL = 20*TIME_DEFAULT  #S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL)