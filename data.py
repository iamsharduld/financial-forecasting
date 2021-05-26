# Cypto Data
# Source - https://www.cryptodatadownload.com/data/gemini/

import pandas as pd
import pandas_datareader as web
import datetime as dt
import yfinance as yf

BTC_CSV_URL = 'https://www.cryptodatadownload.com/cdd/gemini_BTCUSD_1hr.csv'
ETH_CSV_URL = 'https://www.cryptodatadownload.com/cdd/gemini_ETHUSD_1hr.csv'
LTH_CSV_URL = 'https://www.cryptodatadownload.com/cdd/gemini_LTCUSD_1hr.csv'

CRYPTO_SYMBOLS = {
    'BTC': {
        'URL': 'https://www.cryptodatadownload.com/cdd/gemini_BTCUSD_1hr.csv',
        'Name': 'Bitcoin'
    },
    'ETH': {
        'URL': 'https://www.cryptodatadownload.com/cdd/gemini_ETHUSD_1hr.csv',
        'Name': 'Ethereum'
    },
    'LTH': {
        'URL': 'https://www.cryptodatadownload.com/cdd/gemini_LTCUSD_1hr.csv',
        'Name': 'Litecoin'
    }
}

COLUMN_FILTERS = ["Date", "Open"]



def get_crypto_data(symbol='BTC', interval='1h', period='30d'):
    
    df = pd.read_csv(CRYPTO_SYMBOLS[symbol]['URL'], header=1)
    df_filtered = df[COLUMN_FILTERS]
    df_filtered = df_filtered.iloc[::-1]
    n = len(df_filtered)
    df_filtered.iloc[::1, :]
    
    if(interval[-1] == 'h'):
        hours = int(interval.split('h')[0])
    if(interval[-1] == 'd'):
        hours = int(interval.split('d')[0])
        hours *= 24
    interval = hours
        
    if(period[-1] == 'h'):
        hours = int(period.split('h')[0])
    if(period[-1] == 'd'):
        hours = int(period.split('d')[0])
        hours *= 24
    period = hours
    
    return df_filtered.tail(period).iloc[::int(interval), :]

# get_crypto_data(symbol='BTC', interval='1h', period='1100d')


