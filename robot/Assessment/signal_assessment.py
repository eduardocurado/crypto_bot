from robot.Extractor import longPositions
from datetime import datetime, timedelta


def assignment_sell(coin):
    open_positions = longPositions.get_positions(coin, 'active')
    if open_positions.empty:
        return False
    return True


def assignment_buy(balance, date, coin):
    # open_positions = longPositions.get_all_longs(coin)
    size = 100
    open_positions = longPositions.get_positions(coin, 'active')
    date_now = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    last_date_now = date_now - timedelta(hours=16)
    if len(open_positions):
        _current = open_positions[(open_positions['date_ask'] >= last_date_now)
                                  & (open_positions['date_ask'] <= date_now)]
        sizes = [100, 80, 60, 40]
        if len(_current) <= 4:
            size = sizes[len(_current)-1]
    if balance >= size:
        print("Entry Size")
        return size
    print("Refused due to no money")
    print(balance)
    return 0
