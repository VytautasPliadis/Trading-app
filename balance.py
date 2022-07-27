import kucoin.client
from kucoin.client import Client
import requests
import os
from dotenv import load_dotenv 
load_dotenv()

import requests
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode
import time

if not os.getenv('api_key') or os.getenv('api_secret') or os.getenv('api_passphrase'): 
    raise Exception("Please provide env. variables: api_key, api_secret, api_passphrase, mongodb_password")

#Kucoin client
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
api_passphrase = os.getenv('api_passphrase')
client = Client(api_key, api_secret, api_passphrase)
base_uri = 'https://api.kucoin.com'

def get_headers(method, endpoint):
    now = int(time.time() * 1000)
    str_to_sign = str(now) + method + endpoint
    signature = base64.b64encode(hmac.new(api_secret.encode(), str_to_sign.encode(), hashlib.sha256).digest()).decode()
    passphrase = base64.b64encode(hmac.new(api_secret.encode(), api_passphrase.encode(), hashlib.sha256).digest()).decode()
    return {'KC-API-KEY': api_key,
            'KC-API-KEY-VERSION': '2',
            'KC-API-PASSPHRASE': passphrase,
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': str(now)
    }

method = 'GET'
# endpoint = '/api/v1/symbols'   #alternative endpoint
endpoint = '/api/v1/symbols?status=active'
response = requests.request(method, base_uri+endpoint, headers=get_headers(method,endpoint))
print(response.status_code)
info = response.json()    

def last_bought_price(pair):
    pair = pair.replace('/','-')
    orders = client.get_fills(symbol=pair, side='buy') #symbol='BTC-USDT'
    orders = orders.get('items')
    order=orders[0]
    orderPrice=order.get('price')
    orderPrice=float(orderPrice)
    return orderPrice

def account(id):
    balance = client.get_accounts(currency, account_type)
    balance = balance[0]
    cryptoName = balance.get('currency')
    cryptoQuantity = balance.get('available')
    return cryptoName, cryptoQuantity

def get_current_price(pair):
    pair = pair.replace('/','-')
    pair = client.get_ticker(pair)
    price = pair.get('price')
    price_round = price.split('.')
    try:
        price_round = len(price_round[1])
    except:
        price_round = 0
    return price, price_round

def buy(usdtQuantity,pair):
    pairsList = info.get('data')
    for p in pairsList:
        symbol=p.get('symbol')
        if symbol == pair:
            minQty=p.get('baseIncrement')
            minQty_2 = str(minQty)
            minQty_2 = minQty_2.split('.')
            minQtyRound = len(minQty_2[1])
    usdtRound=float(usdtQuantity)
    usdtRound=int(usdtRound)
    print('START BUYING....'+str(pair))
    try:
        order = client.create_market_order(pair, client.SIDE_BUY, funds = usdtRound)
        time.sleep(2)
        orderDetails = client.get_order(order["orderId"])
        price = float(orderDetails["dealFunds"]) / float(orderDetails["dealSize"])
        boughtQuantity = float(orderDetails["dealSize"])

        msg = f"Bought {pair}: {boughtQuantity}: {price} USDT "
        print(msg)

        currentCryptoPrice = balance.get_current_price(pair)
        currentCryptoPrice = currentCryptoPrice[0]            
        currentCryptoPriceRound = currentCryptoPrice[1]            


        profitPrice= price * 1.15
        profitPrice = round(profitPrice, currentCryptoPriceRound)

    except:
        print('BUYING ERROR')
        pass

    try:
        time.sleep(2)
        boughtQuantity = round(boughtQuantity,minQtyRound)-float(minQty) 
        boughtQuantity = round(boughtQuantity,minQtyRound)
        msg = f"PLACING SELL LIMIT ORDER {pair} {boughtQuantity} AT: {profitPrice} USDT"
        print(msg)
        order = client.create_limit_order(pair, client.SIDE_SELL, profitPrice, boughtQuantity)
        print('OK')

    except:
        print('SELL LIMIT ERROR')
        pass


def sell(usdtQuantity,pair):
    pairsList = info.get('data')
    #print(pairsList)
    for p in pairsList:
        symbol=p.get('symbol')
        pair=pair.replace('/','-')
        if symbol == pair:
            minQty=p.get('baseIncrement')
            minQty = str(minQty)
            minQty = minQty.split('.')
            minQtyRound = len(minQty[1])
    usdtRound=float(usdtQuantity)
    usdtRound=round(usdtRound,minQtyRound)
    print('START SELLING'+str(pair)+' '+str(usdtRound))
    try:
        order = client.create_market_order(pair, client.SIDE_SELL, funds = usdtRound)
        orderDetails = client.get_order(order["orderId"])
        price = float(orderDetails["dealFunds"]) / float(orderDetails["dealSize"])
        boughtQuantity = float(orderDetails["dealSize"])
        print('OK')
    except:
        print('SELLING ERROR')
