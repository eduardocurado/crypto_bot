from datetime import datetime, timedelta
import time
from robot.Poloniex import feeder
from robot.Utils import Initializations
from robot.Decision import features, exit, enter
from robot.Extractor import longPositions, tickers
from robot.Assessment import signal_assessment
from robot.Utils import services


def set_up_bd(coin, start):
    start_timer = datetime.now()
    print('Setting up BD')
    Initializations.drop_all_tables('postgres', '', 'robotdb')
    Initializations.create_all_tables('postgres', '', 'robotdb')
    print('Feeding base data')
    size_historical = feeder.get_historical_data(coin, start)
    print('Feeding screen 1')
    feeder.get_historical_screen(4, coin, 1)
    print('Feeding screen 2')
    feeder.get_historical_screen(24, coin, 2)
    return size_historical


def main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    start = (datetime.now() - timedelta(days=45)).timestamp()
    coin = 'BTC_ETH'
    size_bd = set_up_bd(coin, start)
    print(size_bd)
    balance = 1
    entry_size = balance / 10
    start = datetime.now()
    print(start)
    tickers_df = tickers.get_all_tickers(coin, 0)
    initial_tick = tickers_df.iloc[0]
    longPositions.enter_positions(TIME_DEFAULT_COUNT,
                                  coin,
                                  entry_size,
                                  initial_tick.date,
                                  initial_tick.price,
                                  initial_tick.price*(1+0.15),
                                  initial_tick.price*(1-0.1))
    balance -= entry_size
    for index, row in tickers_df.iterrows():
        open_positions = longPositions.get_positions(coin, 'active')
        last_date = row.date.strftime("%Y-%m-%d %H:%M:%S")
        last_price = row.price
        if not open_positions.empty:
            exits = exit.strategy_one(last_price, last_date, coin, open_positions)
            if exits:
                print('Has open position')
                print('EXITING POSITION')
                services.execute_order()
                longPositions.exit_positions(exits)
                features.update_balance()
                balance += entry_size * len(exits)
                longPositions.update_stop_loss()
                longPositions.update_take_profit()

        TIME_DEFAULT_COUNT += 1
        if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL or not TIME_DEFAULT_COUNT % LONG_INTERVAL:
            if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL:
                # entry_sign = enter.strategy_one(coin, last_date, last_price)
                entry_sign = enter.strategy_two(coin, last_date, last_price)
                if entry_sign:
                    if entry_sign.get('signal') == 'BUY':
                        if signal_assessment.assignment_buy(coin, balance):
                            print('BUY')
                            services.execute_order()
                            longPositions.enter_positions(TIME_DEFAULT_COUNT,
                                                          coin,
                                                          balance,
                                                          last_date,
                                                          last_price,
                                                          entry_sign.get('take_profit'),
                                                          entry_sign.get('stop_loss')
                                                          )
                            features.update_balance()
                            balance -= entry_size
                    elif entry_sign.get('signal') == 'SELL':
                        if signal_assessment.assignment_sell(coin):
                            open_positions = longPositions.get_positions(coin, 'active')
                            if open_positions.empty:
                                continue
                            else:
                                exits = []
                                for index_open, row_open in open_positions.iterrows():
                                    exits.append({'id': row_open.id_position,
                                                  'coin': coin,
                                                  'source': "sell_sign",
                                                  'exit_price': last_price,
                                                  'size_position': row_open.size_position
                                                  })
                                print('SELL')
                                services.execute_order()
                                longPositions.exit_positions(exits)
                                features.update_balance()
                                balance += entry_size * len(exits)


def main(TIME_DEFAULT, INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    coin = 'BTC_ETH'
    balance = 0.002189393483
    start = datetime.now()
    print(start)

    while 1:
        time.sleep(TIME_DEFAULT)
        tick, last_date = feeder.get_tick(coin)
        if not tick:
            print("ERROR")
            continue
        print(tick)
        open_positions = longPositions.get_positions(coin, 'active')
        if not open_positions.empty:
            print('Has open position')
            exits = exit.strategy_one(tick, last_date, coin, open_positions)
            if exits:
                print('EXITING POSITION')
                services.execute_order()
                longPositions.exit_positions(exits)
                features.update_balance()
        longPositions.update_stop_loss()
        longPositions.update_take_profit()
        features.update_indicators(last_date, coin, 0)
        TIME_DEFAULT_COUNT += 1

        if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL or not TIME_DEFAULT_COUNT % LONG_INTERVAL:
            if not TIME_DEFAULT_COUNT % INTERMEDIATE_INTERVAL:
                features.update_screen(INTERMEDIATE_INTERVAL, coin, 1)
            if not TIME_DEFAULT_COUNT % LONG_INTERVAL:
                features.update_screen(LONG_INTERVAL, coin, 2)

            entry_sign = enter.strategy_one()
            if entry_sign == 'BUY':
                if signal_assessment.assignment():
                    print('BUY')
                    services.execute_order()
                    longPositions.enter_positions(TIME_DEFAULT_COUNT, coin, balance, last_date, tick)
                    features.update_balance()
            elif entry_sign == 'SELL':
                if signal_assessment.assignment():
                    print('SELL')
                    services.execute_order()
                    longPositions.exit_positions(TIME_DEFAULT_COUNT, coin, balance, last_date, tick)
                    features.update_balance()


TIME_DEFAULT = 5
INTERMEDIATE_INTERVAL = 20*TIME_DEFAULT  #S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL)
