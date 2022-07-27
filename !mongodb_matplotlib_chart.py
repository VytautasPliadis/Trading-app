import certifi
import pymongo
from pymongo import MongoClient 
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
now = datetime.now()
currentTime = now.strftime('%m-%d %H:%M')
deltatime = now - timedelta(days = 7)
deltatime = deltatime.strftime('%m-%d')
deltatime = deltatime + '\W.....'

from dotenv import load_dotenv 
import os
load_dotenv()

CONNECTION_STRING = 'mongodb+srv://Velvetas:' + os.getenv('mongodb_password') + '@cluster0.wtpjebr.mongodb.net/?retryWrites=true&w=majority'
cluster = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db = cluster["Test"]
collection = db["Portfolio"]

#Delete 
# collection.delete_many({})
# collection.delete_many({"date": {"$regex": deltatime}})

# count=collection.count_documents({})

#Post to Mongodb
# post = {"total" :250,"date":currentTime}
# collection.insert_one(post)					

results = collection.find({})
totalAssets = list()
totalDate = list()

for result in results:
	totalAssets.append(result["total"])
	totalDate.append(result["date"])

fig, ax = plt.subplots()
ax.plot(totalDate,totalAssets)
# ax.set(xlabel='Time', ylabel='USD',
# title='Total assets')
# ax.grid()
plt.show()