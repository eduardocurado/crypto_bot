import time
from datetime import datetime
from robot.Poloniex import feeder
from robot.Utils import Initializations
from robot.Decision import features, exit, enter
from robot.Extractor import longPositions, tickers, balances
from robot.Assessment import signal_assessment
from robot.Utils import services, Plots


def main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL):
    TIME_DEFAULT_COUNT = 0
    coins = ['USDT_BTC']
    days = 300
    balance = 1000
    entry_size = balance / 10
    restored = Initializations.set_up_bd(days)

    if not restored:
        for coin in coins:
            size_bd = Initializations.feed_historical_data(coin, days)
            print(size_bd)
        Initializations.create_backup(days)

    first_date = tickers.get_all_tickers(0).iloc[0].date
    balances.insert_balance(first_date, 'USD', balance)
    print('Initial balance')
    print(balance)
    tickers_df = tickers.get_all_tickers(0)
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
                revenue = longPositions.exit_positions(exits)
                balance += revenue
                open_positions = longPositions.get_all_status_longs('active')
                print('Total open Positions')
                print(len(open_positions))
                print('Balance')
                print(balance)
                features.update_balance(balance, last_date)
            # else:
            #     longPositions.update_stop_loss(coin, last_price, last_date)

        if (len(tickers_df) - index) < 30:
            continue
        TIME_DEFAULT_COUNT += 1
        tick = tickers.get_ticker(coin, last_date, 1)
        if not tick.empty:
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
                    entry_now = signal_assessment.assignment_buy(balance, last_date, coin)
                    if entry_now:
                        print(entry_now)
                        size = (entry_now / last_price)
                        print('BUY')
                        print(last_date)
                        services.execute_order()
                        longPositions.enter_positions(TIME_DEFAULT_COUNT,
                                                      coin,
                                                      strategy,
                                                      size,
                                                      last_date,
                                                      last_price,
                                                      entry_sign.get('take_profit'),
                                                      entry_sign.get('stop_loss')
                                                      )
                        balance = balance - entry_now - entry_now * 0.0025
                        open_positions = longPositions.get_all_status_longs('active')
                        print(last_date)
                        print('Total open Positions')
                        print(len(open_positions))
                        print('Balance')
                        print(balance)
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
                            balance += entry_size * len(exits) #does not yet include taxes

            longPositions.update_stop_loss(coin, last_price, last_date)
            open_positions = longPositions.get_all_status_longs('active')
            closed_positions = longPositions.get_all_status_longs('closed')
            print(last_date)
            print('Total Positions')
            print((len(open_positions) +len(closed_positions)))
            print('Total open Positions')
            print(len(open_positions))
            print('Balance')
            print(balance)
        features.update_balance(balance, last_date)


TIME_DEFAULT = 5 # MINUTOS
INTERMEDIATE_INTERVAL = 20*TIME_DEFAULT  #S
LONG_INTERVAL = 100*TIME_DEFAULT  # S
main_historical(INTERMEDIATE_INTERVAL, LONG_INTERVAL)
