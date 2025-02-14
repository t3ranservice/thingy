# AVERAGE SELL PRICE:  204.38 204.37 204.37
# SELL 97.2 7.15 5.31 108.7 112.0 7.153 = Money received = 337.513 
# BUY 306.07 39.86 0.96 2.09 2.89 = Money invested = 351.87
# CURRENT 418 
import csv
from collections import defaultdict
from tabulate import tabulate
from decimal import Decimal, getcontext
from pybit.unified_trading import HTTP
import os
import sqlite3
from tradingviewer.logic.queries import *
from tradingviewer.logic.helpers import *
import time
from datetime import datetime

def sql_insert_historical_record(cursor, order, connection):
    cursor.execute("INSERT INTO transactions (spot_pair, direction, filled_value, filled_price, filled_quantity, fee, timestamp, transaction_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
    (order['symbol'], order['side'].upper(), shortfloat(order['execValue']), order['execPrice'], order['execQty'], order['execFee'], order['execTime'], order['execId']))
    connection.commit()

def epoch(days):
    return days * 24 * 60 * 60 * 1000

def get_time_ranges(days_left=7):
    time_ranges = []
    week_delta = epoch(days=7)
    endTime = int(time.time() * 1000)
    while (days_left != 0):
        delta, days_to_substract = (epoch(days=days_left), days_left) if days_left < 7 else (week_delta, 7)
        startTime = endTime - delta
        time_ranges.append({'start_time': startTime, 'end_time': endTime})
        endTime = startTime
        days_left = days_left - days_to_substract
    return time_ranges

def get_latest_records(session, days=51):
    time_ranges = get_time_ranges(days)
    data = []
    cursor = ""
    for time_range in time_ranges:
        while(True):
            response = session.get_executions(category="spot",cursor=cursor, startTime=time_range['start_time'], endTime=time_range['end_time'])
            # print(response)
            if response['result']['list']:
                data.append(response["result"])
            cursor = response["result"]["nextPageCursor"]
            if cursor == "":
                print("Next cursor is empty, quiting...")
                break
    return data


def display_table(data):
    # Prepare table rows
    table = []
    for spot_pair, values in data.items():
        table.append([
            spot_pair,
            shortfloat(values['Total spent']),
            shortfloat(values['Raw received']),
            Decimal(values['Average buy price'] / values['Counter']).quantize(Decimal('1.0000000000')) if values['Average buy price'] > 0 else 0,
            Decimal(values['Average sell price'] / values['Counter']).quantize(Decimal('1.0000000000')) if values['Average sell price'] > 0 else 0,
            values['Counter'],
            values['Value held'] if 'Value held' in values else 0,
            shortfloat(values['Profit'])
        ])
    
    headers = ['Spot Pair', 'Total Spent', 'Raw Received', 'Average Buy Price', 'Average Sell Price', 'Counter', 'Value held', 'Profit']
    
    print(tabulate(table, headers=headers, tablefmt='pretty'))
    

def process_data():
    final_dict = defaultdict(lambda: {'Total spent': 0, 'Raw received': 0,
                                      'Counter': 0, 'Average buy price': 0, 'Average sell price': 0, 'Profit': 0, 'Value held': 0})
    session = HTTP(
        testnet=False,
        api_key=os.getenv('BYBIT_KEY'),
        api_secret=os.getenv('BYBIT_SECRET')
    )
    response = session.get_wallet_balance(accountType="UNIFIED")

    for row in response['result']['list'][0]['coin']:
        spot_pair = f"{row['coin']}USDT"
        if spot_pair == "USDTUSDT":
            pass
        else:
            final_dict[spot_pair]['Value held'] = float(row['usdValue'])
    
    print(os.getcwd())
    with open('./tradingviewer/logic/123.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            spot_pair = row['Spot Pairs']
            final_dict[spot_pair]['Counter'] += 1
            if row['Direction'] == "BUY":
                final_dict[spot_pair]['Total spent'] += shortfloat(row['Filled Value'])
                final_dict[spot_pair]['Average buy price'] += Decimal((row['Filled Price']))
            else:
                final_dict[spot_pair]['Raw received'] += shortfloat(row['Filled Value'])
                final_dict[spot_pair]['Average sell price'] += Decimal((row['Filled Price']))

    for k, v in final_dict.items():
        final_dict[k]["Profit"] = final_dict[k]['Raw received'] + final_dict[k]['Value held'] - final_dict[k]['Total spent']
    final_dict = dict(sorted(final_dict.items(), key=lambda item: item[1]["Profit"], reverse=True))

    return final_dict

def process_csv(csvfile, connection):
     cursor = connection.cursor()
     with open(csvfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("INSERT INTO historical_data (spot_pair, filled_value, filled_price, direction, timestamp, transaction_id) VALUES(?, ?, ?, ?, ?, ?)",
                           (row['Spot Pairs'], shortfloat(row['Filled Value']), row['Filled Price'], row['Direction'], convert_epoch(row['Timestamp (UTC+0)']), row["Transaction ID"] ))
            connection.commit()


#https://bybit-exchange.github.io/docs/v5/websocket/private/order
def main():
    data = process_data()
    display_table(data)
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()

    with open('tradingviewer/logic/123.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("INSERT INTO transactions (spot_pair, direction, filled_value, filled_price, filled_quantity, fee, timestamp, transaction_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                           (row['Spot Pairs'], row['Direction'], shortfloat(row['Filled Value']), row['Filled Price'], row['Filled Quantity'], float(row['Fees']) * float(row['Filled Price']), int(datetime.strptime(row['Timestamp (UTC+0)'], "%Y-%m-%d %H:%M:%S").timestamp()), row["Transaction ID"] ))
            connection.commit()

    session = HTTP(
        testnet=False,
        api_key=os.getenv('BYBIT_KEY'),
        api_secret=os.getenv('BYBIT_SECRET')
    )
#     # https://bybit-exchange.github.io/docs/v5/order/order-list - orderStatus == Filled, cumExecValue
    data = get_latest_records(session)
    print(data)
    for page in data:
        for order in page["list"]:
            sql_insert_historical_record(cursor, order, connection)
    connection.close()



if __name__ == "main":
    main()