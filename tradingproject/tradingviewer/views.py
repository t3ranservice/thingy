from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os
import sys
from tradingviewer.logic.main import *
from .models import *



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
    all_transactions = Transaction.objects.all()
    tmp_dict = defaultdict(lambda: {'buy_counter': 0, 'sell_counter': 0, 'average_buy_price': 0, 
                                    'average_sell_price': 0, 'all_buy_volumes': 0, 'all_sell_volumes': 0})
    for transaction in all_transactions:
        if transaction.direction == "BUY":
            tmp_dict[transaction.symbol]['all_buy_prices'] =+ transaction.filled_price
            tmp_dict[transaction.symbol]['all_buy_volumes'] =+ transaction.filled_value
            tmp_dict[transaction.symbol]['buy_counter'] =+ 1
        else:
            tmp_dict[transaction.symbol]['all_sell_prices'] =+ transaction.filled_price
            tmp_dict[transaction.symbol]['all_sell_volumes'] =+ transaction.filled_value
            tmp_dict[transaction.symbol]['sell_counter'] =+ 1

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
