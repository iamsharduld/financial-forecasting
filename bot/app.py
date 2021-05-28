import ccxt
import constants
import websocket, json, pprint
import numpy as np

import random

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

window = 5
closes = [0 for i in range(window)]
moving_avg = 0
cnt = 0

balance_usd = 100000
eth_balance = 0

portfolio_value_in_usd = balance_usd + eth_balance*0

num_dec = 0
num_inc = 0

here = 0


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, moving_avg, cnt, balance_usd, eth_balance
    
    print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message['k']['c'])
    closes.append(float(json_message['k']['c']))
    
    # SMA()


    # adhoc()

    random_choice()

        

def SMA():
    global closes, moving_avg, cnt, balance_usd, eth_balance
    moving_avg = ((moving_avg*window) + (closes[-1]-closes[0]))/float(window)
    closes.pop(0)
    cnt += 1
    profit = 0
    if cnt >= window:
        print(closes)
        print(moving_avg)

        # If moving avg is below current closing price BUY
        if moving_avg < closes[-1] and balance_usd > closes[-1]:
            balance_usd -= closes[-1]
            eth_balance += 1



        # If moving avg is above current closing price SELL
        if moving_avg > closes[-1] and eth_balance > 0:
            balance_usd += closes[-1]
            eth_balance -= 1

            

        portfolio_value_in_usd = balance_usd + eth_balance*closes[-1]
    
        print(balance_usd, eth_balance)
        print(portfolio_value_in_usd)





    # closes.pop(0)
    
# Consecutive falls strat
def adhoc():
    global num_dec, num_inc
    global closes, moving_avg, cnt, balance_usd, eth_balance, here


    print(num_inc, num_dec)
    print(closes[-1], closes[-2])

    if(closes[-1] > closes[-2]):
        num_inc += 1
        num_dec = 0
    
    if(closes[-1] < closes[-2]):
        num_dec += 1
        num_inc = 0

    if(num_inc > 2 and eth_balance > 0):
        balance_usd += closes[-1]*eth_balance
        eth_balance = 0
    
    if(num_dec > 2 and balance_usd > closes[-1]):
        balance_usd -= closes[-1]*3
        eth_balance += 3
        num_dec = 0
            

    portfolio_value_in_usd = balance_usd + eth_balance*closes[-1]

    print(balance_usd, eth_balance)
    print(portfolio_value_in_usd)


# Random
def random_choice():
    global num_dec, num_inc
    global closes, moving_avg, cnt, balance_usd, eth_balance, here

    if random.random() >= 0.5:
        if(eth_balance > 0):
            balance_usd += closes[-1]
            eth_balance -= 1
    else:
        if(balance_usd > closes[-1]):
            balance_usd -= closes[-1]
            eth_balance += 1
    portfolio_value_in_usd = balance_usd + eth_balance*closes[-1]

    print(balance_usd, eth_balance)
    print(portfolio_value_in_usd)







exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': constants.BINANCE_API_KEY,
    'secret': constants.BINANCE_SECRET,
})

binance_markets = exchange.load_markets()


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

