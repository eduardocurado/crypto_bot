from robot.Extractor import longPositions


def assignment_sell(coin):
    open_positions = longPositions.get_positions(coin, 'active')
    if open_positions.empty:
        return False
    return True


def assignment_buy(coin, balance):
    if balance:
        return True
    return False
