from tradingview_ta import TA_Handler, Interval, Exchange
import kucoin.client
from kucoin.client import Client
import re
import os
from dotenv import load_dotenv 
load_dotenv()


#Kucoin client
api_key = os.getenv('api_key')
api_secret = os.getenv('api_secret')
api_passphrase = os.getenv('api_passphrase')
client = Client(api_key, api_secret, api_passphrase)
base_uri = 'https://api.kucoin.com'

def trading_view(pairname):
    kripto = TA_Handler(
        symbol=pairname,
        screener="Crypto",
        exchange="Kucoin",
        interval=Interval.INTERVAL_1_DAY)
    rezoliucija = kripto.get_analysis().summary
    if "STRONG_BUY" in rezoliucija["RECOMMENDATION"]:
        print(rezoliucija["RECOMMENDATION"]+" - "+pairname)
        # print(pairname)
        return pairname

pairs = list()
all_ticks=client.get_symbols()
STABLE_USD = list()

for item in all_ticks:
    kuk_pair=item.get('symbol')
    kuk_pair=kuk_pair.replace('-','/')
    kuk_pair_split=kuk_pair.split('/')
    kuk_pair_stable=kuk_pair_split[0]
    kuk_pair_split=kuk_pair_split[1]
    result = re.search('USD|PAX|3S|3L', kuk_pair_stable)
    if result != None:
        STABLE_USD.append(kuk_pair_stable)

    if kuk_pair_split==('USDT') and kuk_pair_stable not in STABLE_USD:
        kuk_pair=kuk_pair.replace('/','')
        pairs.append(kuk_pair)

if __name__ == "__main__":

    try:
        os.remove("day_pairs.txt")
    except:
        pass

    for i in pairs:
        try:
            # print(i)
            ta_rez=trading_view(i)
            ta_rez= re.split(r'USDT',ta_rez)
            ta_rez = ta_rez[0]+"/USDT"
            with open ('day_pairs.txt',"a") as f:
                f.write(ta_rez+'\n')
        except:
            pass
