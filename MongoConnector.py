import json
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

class MongoConnector(object):
    def __init__(self, db_name, collection_name, host):
        self.host = host
        self.db_name = db_name
        self.collection_name = collection_name
        self.conn = None
        self.collection = None
        self.db = None

    def connect(self):
        try:
            conn = MongoClient(self.host)
            self.db = conn[self.db_name]
            self.collection = self.db[self.collection_name]
        except:
            print("MongoDB bağlanılamadı")
            return False
        print("MongoDB bağlantısı başarılı!!!")
        return True

    def add_cryptos(self, datas):
        # Insert Data
        rec_id1 = self.collection.insert_many(datas)
        print("Data inserted with record ids", rec_id1)

    def get_crypto_data_by_asset_in_24_hours(self, asset):
        search_time = datetime.now() + timedelta(hours=-24)
        return self.collection.find(
            {"ts": {"$gt": search_time},
             "metadata": {"asset": asset, "symbol": "{}-USD".format(asset)}
             })

        # Printing the data inserted
        # cursor = self.collection.find({"metadata": {"asset": "ETH", "symbol": "ETH-USD"}})
        # print("search_time:", search_time)
        # cursor = self.collection.find({"ts": {"$gt": search_time}, "metadata": {"asset": "ETH", "symbol": "ETH-USD"} })
        # for record in cursor:
        #     print(record)