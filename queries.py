from helpers import *

def sql_insert_historical_record(cursor, order, connection):
    cursor.execute("INSERT INTO historical_data (spot_pair, filled_value, filled_price, direction, timestamp, transaction_id) VALUES(?, ?, ?, ?, ?, ?)",
    (order['symbol'], shortfloat(order['execValue']), order['execPrice'], order['side'].upper(), order['execTime'], order['execId']))
    connection.commit()