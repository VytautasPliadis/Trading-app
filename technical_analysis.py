import pandas as pd
import pandas_ta as ta
import ccxt
exchange = ccxt.kucoin()

def get_indicators(asset,laikas):
	try:
		bars = exchange.fetch_ohlcv(asset, timeframe=laikas, limit=100)
		df = pd.DataFrame(bars, columns=['Time','Open','High','Low','Close','Volume'])
		idx = 0
		new_col = asset  # can be a list, a Series, an array or a scalar
		df.insert(loc=idx, column='PAIR', value=new_col)
		df = df.dropna()
		df.Close = df.Close.astype(float)
		df.Time = pd.to_datetime(df.Time, unit='ms')

		RSI = df.ta.rsi(22)
		RSI_EMA = df.ta.ema(close=df.ta.rsi(22), length=12, append=False)
		RSI_HOTNESS = RSI - RSI_EMA
			
		df = pd.concat([df,RSI_HOTNESS.rename('RSI_HOTNESS')],axis=1)
		df=df.iloc[-1:]
		return df
	except:
		print('ERROR '+asset)
		pass

def apply_ta(pairsList,timeframe):
	df=pd.DataFrame()
	pairsLenght=len(pairsList)
	count = 0
	print('CALULATING INDICATORS '+str(timeframe))
	for i in range(len(pairsList)):
		x=get_indicators(pairsList[i],timeframe)
		df = df.append(x, ignore_index = True)
		count += 1
		print(count,'of',pairsLenght)
	df=df.sort_values(by=['RSI_HOTNESS'], ascending=True)
	df.head()
	taResults = df.iloc[:, 0].tolist()
	resultsToReturn=list()
	for i in taResults:
		i=i.replace('/','-')
		resultsToReturn.append(i)
	if len(resultsToReturn) == 0:
		print('NOTHING TO BUY')
	else:
		return resultsToReturn