from datetime import datetime, timedelta
import time

import pandas as pd
from robot.Poloniex import feeder
from robot.Utils import Initializations
from robot.Decision import features, exit, enter
from robot.Extractor import longPositions, tickers
from robot.Assessment import signal_assessment
from robot.Utils import services, Plots


def main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    coins = ['USDT_BTC', 'USDT_LTC']
    days = 60
    balance = 500000000
    entry_size = balance / 10
    restored = Initializations.set_up_bd(days)

    if not restored:
        for coin in coins:
            size_bd = Initializations.feed_historical_data(coin, days)
            print(size_bd)
        Initializations.create_backup(days)

    tickers_df = tickers.get_all_tickers(1)
    # tickers_df = tickers.get_all_tickers_screen('USDT_BTC', 1)
    for index, row in tickers_df.iterrows():
        last_date = row.date.strftime("%Y-%m-%d %H:%M:%S")
        last_price = row.price
        coin = row.coin
        open_positions = longPositions.get_positions(coin, 'active')

        if not open_positions.empty:
            exits = exit.strategy_one(last_price, last_date, coin, open_positions)
            if exits:
                print('Has open position')
                print('EXITING POSITION')
                services.execute_order()
                longPositions.exit_positions(exits)
                features.update_balance(coin)
                balance += entry_size * len(exits)
            else:
                longPositions.update_stop_loss(coin, last_price)

        if index < 30:
            continue
        TIME_DEFAULT_COUNT += 1
        if tickers.get_ticker(coin, last_date, 1):
            cross_over = None
            channel = None
            rsi = None
            #cross_over = enter.cross_over_strategy(coin, last_date, last_price)
            channel = enter.channel_strategy(coin, last_date, last_price)
            #rsi = enter.rsi_strategy(coin, last_date, last_price)
            if channel or cross_over or rsi:
                if channel:
                    strategy = 'CHANNEL'
                    entry_sign = channel
                elif rsi:
                    strategy = 'RSI'
                    entry_sign = rsi
                elif cross_over:
                    strategy = 'CROSS_OVER'
                    entry_sign = cross_over

                if entry_sign.get('signal') == 'BUY':
                    if signal_assessment.assignment_buy(balance):
                        print('BUY')
                        services.execute_order()
                        longPositions.enter_positions(TIME_DEFAULT_COUNT,
                                                      coin,
                                                      strategy,
                                                      entry_size,
                                                      last_date,
                                                      last_price,
                                                      entry_sign.get('take_profit'),
                                                      entry_sign.get('stop_loss')
                                                      )
                        features.update_balance(coin)
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
                                              'ask_date': last_date,
                                              'size_position': row_open.size_position
                                              })
                            print('SELL')
                            services.execute_order()
                            longPositions.exit_positions(exits)
                            features.update_balance(coin)
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
            exits = exit.strategy_one(tick, last_date, coin, open_positions)
            if exits:
                print('EXITING POSITION')
                services.execute_order()
                longPositions.exit_positions(exits)
                features.update_balance(coin)
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
                    features.update_balance(coin)
            elif entry_sign == 'SELL':
                if signal_assessment.assignment():
                    print('SELL')
                    services.execute_order()
                    longPositions.exit_positions(TIME_DEFAULT_COUNT, coin, balance, last_date, tick)
                    features.update_balance(coin)


TIME_DEFAULT = 5 # MINUTOS
INTERMEDIATE_INTERVAL = 20*TIME_DEFAULT  #S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL)
