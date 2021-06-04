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


num_dec = 0
num_inc = 0

here = 0

account = {
    'ETH': {
        'balance': 0
    },
    'BTC': {
        'balance': 0
    },
    'USD': {
        'balance': 100000
    }
}

portfolio_value_in_usd = account['USD']['balance']


symbol_data_map = {
    'ETH': 'ETH/USDT',
    'BTC': 'BTC/USDT'
}


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


def buy(symbol, exchange_rate, quantity):
    global account
    if account['USD']['balance'] < exchange_rate * quantity:
        # print(f'Insufficient Balance USD')
        return

    account['USD']['balance'] -= (exchange_rate * quantity)
    account[symbol]['balance'] += quantity


def sell(symbol, exchange_rate, quantity):
    global account


    if quantity == 'all':
        account['USD']['balance'] += account[symbol]['balance'] * exchange_rate
        account[symbol]['balance'] = 0
        # print(f'Insufficient Balance {symbol}')
        return

    if account[symbol]['balance'] < quantity:
        # print(f'Insufficient Balance {symbol}')
        return


    account[symbol]['balance'] -= quantity
    account['USD']['balance'] += quantity * exchange_rate

# Strat 1 - Random Choice
def random_choice(symbol, last_close):
    global account, portfolio_value_in_usd

    if random.random() >= 0.5:
        sell(symbol, last_close, 1)
    else:
        buy(symbol, last_close, 1)
    portfolio_value_in_usd = account['USD']['balance'] + account[symbol]['balance']*last_close
    # print(portfolio_value_in_usd)
    # print(account)

# Strat 2 - SMA
prev_closes = []
def simple_moving_avg(symbol, last_close, duration=5):
    global account, portfolio_value_in_usd

    prev_closes.append(last_close)
    # print(prev_closes)
    if len(prev_closes) < duration+1:
        # print(prev_closes)
        return

    # print(last_close, np.mean(prev_closes))
    if last_close < np.mean(prev_closes[len(prev_closes)-duration:]):
        buy(symbol, last_close, 1)
    else:
        sell(symbol, last_close, 1)


    portfolio_value_in_usd = account['USD']['balance'] + account[symbol]['balance']*last_close
    # print(portfolio_value_in_usd)
    # print(last_close, np.mean(prev_closes[len(prev_closes)-duration:] ), portfolio_value_in_usd)
    # print(account)


# Strat 3 - Change of difference of closing prices
# When difference of close prices changes from negative to positive, BUY
# When difference of close prices changes from positive to negative, SELL
# Result -> High change transformed to lower change eg. 15% gain -> 3 % gain, -10% loss -> -2% loss
last_3_closes = []
last_buy = -1
last_sell = -1
total_rev = 0
def change_of_diff(symbol, last_close):

    global portfolio_value_in_usd, last_3_closes, last_buy, last_sell, total_rev

    if(len(last_3_closes) < 3):
        last_3_closes.append(last_close)
        return
    else:
        last_3_closes.pop(0)
        last_3_closes.append(last_close)

    print(last_3_closes, last_3_closes[1] - last_3_closes[0], last_3_closes[2] - last_3_closes[1])
    # print(last_3_closes[1] - last_3_closes[0], last_3_closes[2] - last_3_closes[1])
    if (last_3_closes[1] - last_3_closes[0] < 0) and (last_3_closes[2] - last_3_closes[1] > 0):
        last_buy = last_3_closes[2]
        buy(symbol, last_3_closes[2], 1)

    if (last_3_closes[1] - last_3_closes[0] > 0) and (last_3_closes[2] - last_3_closes[1] < 0):
        sell(symbol, last_3_closes[2], 1)
        print(f"SELL {last_3_closes[2]}, last BUY {last_buy}")
        print(last_buy - last_3_closes[2], total_rev)
        if last_buy != -1:
            total_rev += (last_3_closes[2] - last_buy)

    portfolio_value_in_usd = account['USD']['balance'] + account[symbol]['balance']*last_3_closes[2]



def reset():
    global account, portfolio_value_in_usd
    account = {
        'ETH': {
            'balance': 0
        },
        'BTC': {
            'balance': 0
        },
        'USD': {
            'balance': 100000
        }
    }
    portfolio_value_in_usd = account['USD']['balance']


def get_data(symbol):
    binance = ccxt.binance()
    # each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
    return binance.fetchOHLCV(symbol_data_map[symbol], timeframe='5m', params={})

def backtest(symbol, strategy):
    global balance_usd, eth_balance, portfolio_value_in_usd, total_rev
    data = get_data(symbol)
    print(type(strategy))
    print(strategy)
    # print(data)
    for candle in data:
        if strategy.__name__ == 'simple_moving_avg':
            strategy(symbol, candle[1], duration=5)

        if strategy.__name__ == 'random_choice':
            strategy(symbol, candle[1])

        if strategy.__name__ == 'change_of_diff':
            strategy(symbol, candle[4])

    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[-1][0]/1000))
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0][0]/1000))

    print(f"Backtest Results: {total_rev}")
    print()
    print(f'Start time: {start_time}, End time: {end_time}')
    print(f'Start price: {data[0][1]}, End price: {data[-1][1]}')
    print(f'Price difference: {data[-1][1] - data[0][1]}')
    print()
    print(f"{symbol} percent change {(100*(data[-1][1] - data[0][1])/float(data[0][1]))}")
    print(f"Gain / Loss in percent {(100*(portfolio_value_in_usd-100000)/float(100000))}")
    print(account)
    print(portfolio_value_in_usd)
    reset()




exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': constants.BINANCE_API_KEY,
    'secret': constants.BINANCE_SECRET,
})

binance_markets = exchange.load_markets()

backtest('BTC', change_of_diff)
# ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
# ws.run_forever()

