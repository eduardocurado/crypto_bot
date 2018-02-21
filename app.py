from datetime import datetime

from robot.Poloniex import extractor
from robot.Utils import Initializations


def main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    Initializations.drop_all_tables('postgres', '', 'robotdb')
    Initializations.create_all_tables('postgres', '', 'robotdb')
    start = datetime.now()
    size_historical = extractor.get_historical_data('BTC_ETH')
    coin = 'BTC_ETH'
    extractor.get_historical_screen(size_historical, 4, 'BTC_ETH', 1)
    extractor.get_historical_screen(size_historical, 24, 'BTC_ETH', 2)


    # while 1:
    #     time.sleep(TIME_DEFAULT)
    #     services.feed_data('BTC_ETH')
    #     features.update_indicators(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), coin, 0)
    #     TIME_DEFAULT_COUNT += 1
    #
    #     if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL:
    #         features.update_screen(INTERMEDIATE_INTERVAL, coin, 1)
    #
    #     if not TIME_DEFAULT_COUNT % LONG_INTERVAL:
    #         features.update_screen(LONG_INTERVAL, coin, 2)


TIME_DEFAULT = 15
INTERMEDIATE_INTERVAL = 20*TIME_DEFAULT  # S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
start = datetime.now()
main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL)
end = datetime.now()