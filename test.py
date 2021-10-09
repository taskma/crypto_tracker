from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")

# db = client.test
db = client["crypto_db"]
collection = db["crypto_series"]
datas = {"test1": "testyigit"}
rec_id1 = collection.insert_one(datas)
print("Data inserted with record ids", rec_id1)