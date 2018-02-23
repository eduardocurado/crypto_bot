from robot.Extractor import longPositions


def assignment_sell(coin):
    open_positions = longPositions.get_open_positions(coin)
    if open_positions.empty:
        return False
    return True


def assignment_buy(coin):
    pass
