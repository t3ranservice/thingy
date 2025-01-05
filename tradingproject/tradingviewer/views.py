from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os
import sys
from tradingviewer.logic.main import *
from .models import *
from itertools import zip_longest



def index(request):

    return render(request, 'tradingviewer/index.html')


def process_data_plain(request):
    if request.method == "POST":
        input_value = int(request.POST.get('input_number', 0))
        
        session = HTTP(
            testnet=False,
            api_key=os.getenv('BYBIT_KEY'),
            api_secret=os.getenv('BYBIT_SECRET')
        )
        data = get_latest_records(session, days=input_value)
        for page in data:
                for order in page["list"]:
                    try:
                        Transaction.objects.create(
                            symbol=order['symbol'],
                            direction=order['side'].upper(),
                            filled_value=shortfloat(order['execValue']),
                            filled_price=order['execPrice'],
                            filled_quantity=order['execQty'],
                            fee=order['execFee'],
                            timestamp=order['execTime'],
                            transaction_id=order['execId']
                        )
                    except:
                        print("Transaction already exists, skipping..")
    return render(request, 'tradingviewer/process_data.html')


def process_data_table(request):
    data = process_data()
    display_table(data)
    return HttpResponse(display_table(data))

def test_endpoint(request):
    final_dict = defaultdict(lambda: {'average_buy_price': 0, 'average_sell_price': 0,
                                      'net': 0})
    all_transactions = Transaction.objects.all()
    tmp_dict = defaultdict(lambda: {'buy_counter': 0, 'sell_counter': 0, 'all_buy_prices': 0, 
                                    'all_sell_prices': 0, 'all_buy_volumes': 0, 'all_sell_volumes': 0, 'current_value_usdt': 0, })
    session = HTTP(
            testnet=False,
            api_key=os.getenv('BYBIT_KEY'),
            api_secret=os.getenv('BYBIT_SECRET')
        )    
    
    for transaction in all_transactions:
        if transaction.direction == "BUY":
            tmp_dict[transaction.symbol]['all_buy_prices'] += transaction.filled_price
            tmp_dict[transaction.symbol]['all_buy_volumes'] += transaction.filled_value
            tmp_dict[transaction.symbol]['buy_counter'] += 1
        else:
            tmp_dict[transaction.symbol]['all_sell_prices'] += transaction.filled_price
            tmp_dict[transaction.symbol]['all_sell_volumes'] += transaction.filled_value
            tmp_dict[transaction.symbol]['sell_counter'] += 1

    wallet_balance = session.get_wallet_balance(accountType="UNIFIED")

    for row in wallet_balance['result']['list'][0]['coin']:
        spot_pair = f"{row['coin']}USDT"
        if spot_pair == "USDTUSDT":
            pass
        else:
            tmp_dict[spot_pair]['current_value_usdt'] = float(row['usdValue'])
            tmp_dict[spot_pair]['current_value_asset'] = float(row['equity'])
    
    for key, value in tmp_dict.items():
        AssetData.objects.update_or_create(symbol=key, average_buy_price=((value['all_buy_prices']/value['buy_counter']) if value['buy_counter'] != 0 else 0),
                                 average_sell_price=((value['all_sell_prices']/value['sell_counter']) if value['sell_counter'] != 0 else 0), net=(value['all_buy_volumes']-value['all_sell_volumes']))
    
    for item in AssetData.objects.all():
        final_dict[item.symbol]['average_buy_price'] = item.average_buy_price
        final_dict[item.symbol]['average_sell_price'] = item.average_sell_price
        final_dict[item.symbol]['net'] = item.net + tmp_dict[item.symbol]['current_value_usdt']
        print(f"{item.symbol}: avg-b-p: {item.average_buy_price}, avg-s-p: {item.average_sell_price}, net: {item.net}")
    # print(final_dict)
    # print(final_dict.items())
    # for k,v in final_dict.items():
    #     print(k,v)
    return render(request, 'tradingviewer/index.html', {'context_dict': final_dict.items()})
    return HttpResponse("Test Endpoint. Check console.")

# Average buy price = all_buy_prices/counter
# Average sell price = all_sell_prices/counter
# Currently held (assets) = retrieve from API
# Currently held (USDT) = retrieve from API
# Profit (both realized and unrealized) = all_sell_volumes - all_buy_volumes + current (from API)

# IN DB, WE WILL HAVE ONLY THESE:
# average_buy_price, average_sell_price, net (realized profit)  <---- YES

# Only if new transaction is added, we need to run this recalculation  <--- YES
# Actually easier to set up SQL script on trigger and let it do the job <--- That's how it will be done
# Essentially we need to overwrite a row WHERE user_id & symbol <---- There is a query for overwrite

# We still need 1st time generation anyway <--- YES


# 1 Flow
# Get all transactions -> Disable trigger on asset_data --> Produce asset_data --> Enable trigger back
# New transaction is added, if symbol exists --> Update, if symbol not exists --> Produce and add
