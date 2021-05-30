import ccxt
import constants
import websocket, json, pprint
import numpy as np

import random

import time

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

window = 5
closes = [0 for i in range(window)]
moving_avg = 0
cnt = 0

balance_usd = 100000
eth_balance = 0

prev_value = 100000
first = -1

portfolio_value_in_usd = balance_usd + eth_balance*0

num_dec = 0
num_inc = 0

here = 0


def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, moving_avg, cnt, balance_usd, eth_balance, first
    
    print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message['k']['c'])
    closes.append(float(json_message['k']['c']))

    if(first == -1):
        first = float(json_message['k']['c'])
    
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
    global num_dec, num_inc, prev_value
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

    if(portfolio_value_in_usd > prev_value):
        balance_usd += closes[-1]*eth_balance
        eth_balance = 0
        prev_value = balance_usd

    print(first, closes[-1], closes[-1]-first)
    print(balance_usd, eth_balance)
    print(portfolio_value_in_usd)


# Random
def random_choice(last_close):
    global balance_usd, eth_balance, portfolio_value_in_usd

    if random.random() >= 0.5:
        if(eth_balance > 0):
            balance_usd += last_close
            eth_balance -= 1
    else:
        if(balance_usd > last_close):
            balance_usd -= last_close
            eth_balance += 1
    portfolio_value_in_usd = balance_usd + eth_balance*last_close

    # print(first, last_close, last_close-first)



def get_data():
    binance = ccxt.binance()
    # each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
    return binance.fetchOHLCV('ETH/USDT', timeframe='5m', params={})

def backtest():
    global balance_usd, eth_balance, portfolio_value_in_usd
    data = get_data()

    for candle in data:
        random_choice(candle[1])

    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[-1][0]/1000))
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0][0]/1000))
    print(start_time, end_time)
    print( data[0][1], data[-1][1])
    print(data[-1][1] - data[0][1])
    print()
    print("Indi balance", balance_usd, eth_balance)
    print("Portfolio", portfolio_value_in_usd)
    print()
    print("Ethereum percent change", (100*(data[-1][1] - data[0][1])/float(data[0][1])))
    print("Gain / Loss in percent", (100*(portfolio_value_in_usd-100000)/float(100000)))







exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': constants.BINANCE_API_KEY,
    'secret': constants.BINANCE_SECRET,
})

binance_markets = exchange.load_markets()

backtest()
# ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
# ws.run_forever()

