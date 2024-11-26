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

def floatround(data):
    return round(float(data), 15)

def s_floatround(data):
    return round(float(data), 2)


def display_table(data):
    # Prepare table rows
    table = []
    for spot_pair, values in data.items():
        table.append([
            spot_pair,
            values['Total spent'],
            values['Raw received'],
            Decimal(values['Average buy price'] / values['Counter']).quantize(Decimal('1.000000000000000')) if values['Average buy price'] > 0 else 0,
            Decimal(values['Average sell price'] / values['Counter']).quantize(Decimal('1.000000000000000')) if values['Average sell price'] > 0 else 0,
            values['Counter'],
            values['Value held'] if 'Value held' in values else 0
        ])
    
    # Define table headers
    headers = ['Spot Pair', 'Total Spent', 'Raw Received', 'Average Buy Price', 'Average Sell Price', 'Counter', 'Value held']
    
    # Print the table
    print(tabulate(table, headers=headers, tablefmt='pretty'))
    

def process_data():
    current_assets_dict = defaultdict(lambda: {'Value held': 0})
    final_dict = defaultdict(lambda: {'Total spent': 0, 'Raw received': 0, 'Average Sell Price': 0,
                                      'Counter': 0, 'Average buy price': 0, 'Average sell price': 0})
    session = HTTP(
        testnet=False,
        api_key=os.getenv('BYBIT_KEY'),
        api_secret=os.getenv('BYBIT_SECRET')
    )
    response = session.get_wallet_balance(accountType="UNIFIED")
    with open('file.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            spot_pair = row['Spot Pairs']
            final_dict[spot_pair]['Counter'] += 1
            if row['Direction'] == "BUY":
                if spot_pair == "BONKUSDT":
                    print(f"Price: {Decimal(row['Filled Price'])}")
                final_dict[spot_pair]['Total spent'] += s_floatround((row['Filled Value']))
                final_dict[spot_pair]['Average buy price'] += Decimal((row['Filled Price']))
            else:
                final_dict[spot_pair]['Raw received'] += s_floatround(float(row['Filled Value']))
                final_dict[spot_pair]['Average sell price'] += Decimal((row['Filled Price']))
    for row in response['result']['list'][0]['coin']:
        spot_pair = f"{row['coin']}USDT"
        if spot_pair == "USDTUSDT":
            pass
        else:
            final_dict[spot_pair]['Value held'] = row['usdValue']
    print(final_dict)
    return final_dict


def main():
    view = process_data()
    display_table(view)

    # current_assets_dict = defaultdict(lambda: {})
    # session = HTTP(
    #     testnet=False,
    #     api_key=os.getenv('BYBIT_KEY'),
    #     api_secret=os.getenv('BYBIT_SECRET')
    # )
    # response = session.get_wallet_balance(accountType="UNIFIED")
    
    # for row in response['result']['list'][0]['coin']:
    #     coin = row['coin']
    #     if coin == "USDT":
    #         pass
    #     else:
    #         current_assets_dict[f"{coin}USDT"]['Value held'] = row['usdValue']
    # print(current_assets_dict)



main()