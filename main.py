#!/usr/bin/env python3
import certifi
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta 

import time
import kucoin.client
from kucoin.client import Client
import ccxt
import logging

import requests
import json
import hmac
import hashlib
import base64
from urllib.parse import urlencode

import technical_analysis
import balance

from dotenv import load_dotenv 
import os
load_dotenv()


if not os.getenv('mongodb_password') or os.getenv('api_key') or os.getenv('api_secret') or os.getenv('api_passphrase'): 
    raise Exception("Please provide env. variables: api_key, api_secret, api_passphrase, mongodb_password")


#DateTime
now = datetime.now()
currentTime = now.strftime('%m-%d %H:%M')
deltaTime = now - timedelta(days = 7)
deltaTime = deltaTime.strftime('%m-%d')
deltaTime = deltaTime + '\W.....'

#Mongodb
CONNECTION_STRING = 'mongodb+srv://Velvetas:' + os.getenv('mongodb_password') + '@cluster0.wtpjebr.mongodb.net/?retryWrites=true&w=majority'
cluster = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db = cluster['Test']
collection = db['Portfolio']

#ccxt
exchange = ccxt.kucoin({
    'apiKey': os.getenv('api_key'),
    'secret': os.getenv('api_secret'),
    'password': os.getenv('api_passphrase'),
    })

#Kucoin api
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
api_passphrase = os.getenv('api_passphrase')
client = Client(api_key, api_secret, api_passphrase)

#Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(message)s")
file_handler = logging.FileHandler('logfile.log',mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#custom crypto pairs from text file (BTC/USDT,ETH/USDT...)
pairs = list()
with open ('day_pairs.txt') as file:
    for pair in file:
        pair=pair.strip()
        pairs.append(pair)

#Main script
def main():
    crash = -20
    sellLimit = -15
    minOrderSize = 4

    #Getting acount total balance in USD
    balances = exchange.fetch_accounts()
    currency_prices_lst = client.get_fiat_prices()

    t_total=0
    for i in balances:
        if i.get('info').get('balance') != '0':
            t_amount= i.get('info').get('balance')
            t_symbol = i.get('info').get('currency')
            t_price = currency_prices_lst.get(t_symbol)
            t_total += float(t_amount)*float(t_price)
    total_assets= round(t_total,2)
    logger.debug('TOTAL ASSETS: '+str(total_assets)+' USD\n')
    
    #Post to Mongodb
    post = {"total" :total_assets,"date":currentTime}
    collection.insert_one(post)

    #Delete older than 7 days posts 
    collection.delete_many({"date": {"$regex": deltaTime}})

    kucoin_balance = client.get_account('6060c7bd1a1c7f00066e00d0') #USDT account id
    usdtQuantity = kucoin_balance.get('available')

    #Fetching open sell limit orders
    limitOrders = exchange.fetch_open_orders()
    for i in limitOrders:
        limitOrderName = i.get('symbol')
        limitOrderId = i.get('id')
        limitOrderQuantity = i.get('amount')

        boughtPrice = balance.last_bought_price(limitOrderName)
        currentCrypto = balance.get_current_price(limitOrderName)
        currentCrypto = currentCrypto[0]

        rateOfReturn = ((float(currentCrypto) - float(boughtPrice)) * 100) / float(boughtPrice)
        rateOfReturn = round(rateOfReturn,2)
        logger.debug(limitOrderName +': '+str(rateOfReturn)+'%')

        if rateOfReturn < crash:
            client.cancel_order(limitOrderId)
            time.sleep(2)
            balance.sell(limitOrderQuantity,limitOrderName)
            time.sleep(2)
            code = 'USDT'
            amount = float(usdtQuantity)
            from_ = 'trade';
            to_ = 'main';
            exchange.transfer(code, amount, from_, to_)

        elif rateOfReturn < sellLimit:
            client.cancel_order(limitOrderId)
            time.sleep(2)
            balance.sell(limitOrderQuantity,limitOrderName)
            time.sleep(2)

    #Appying technical analysis on crypto pairs to buy
    if float(usdtQuantity) > minOrderSize:
        pairsToBuy = technicalAnalysis.apply_ta(pairs,'1h')
        z=float(usdtQuantity)//2
        z=int(z)
        pairsToBuy = pairsToBuy[:z]
        usdtToUse = float(usdtQuantity)/len(pairsToBuy)
        usdtToUse = round(usdtToUse,4)

        for i in pairsToBuy:
            balance.buy(usdtToUse,i)
            time.sleep(2)

if __name__ == "__main__":
    main()
