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
import json


def shortfloat(data):
    return round(float(data), 2)


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
    final_dict = defaultdict(lambda: {'Total spent': 0, 'Raw received': 0, 'Average Sell Price': 0,
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
    

    with open('file.csv', newline='') as csvfile:
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
    
    return final_dict

def main():
    view = process_data()
    display_table(view)
    


main()