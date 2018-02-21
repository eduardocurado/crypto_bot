from robot.Extractor import longPositions


def strategy_one(tick, coin):
    exits = []
    open_positions = longPositions.get_open_positions(coin)
    for index, row in open_positions.iterrows():
        print(row)
        take_profit = row.take_profit
        stop_loss = row.stop_loss
        if float(tick) >= take_profit or float(tick) <= stop_loss:
            exits.append(row.id_position)
    return exits
