from robot.Extractor import longPositions


def strategy_one(tick, coin, open_positions):
    exits = []
    for index, row in open_positions.iterrows():
        take_profit = row.take_profit
        stop_loss = row.stop_loss
        if float(tick) >= take_profit:
            exits.append({'id': row.id_position, 'coin': coin,
                          'source': "take_profit",
                          'exit_price': float(tick),
                          'size': row.size
                          })
        elif float(tick) <= stop_loss:
            exits.append({'id': row.id_position,
                          'coin': coin,
                          'source': "stop_loss",
                          'exit_price': float(tick),
                          'size': row.size
                          })
    return exits
