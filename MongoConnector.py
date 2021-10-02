import json
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from CollectionType import CollectionType

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

    def get_crypto_data_by_asset_last_hours(self, asset, hours):
        search_time = datetime.now() + timedelta(hours=-1 * hours)
        collection = self.collection.find(
            {"ts": {"$gt": search_time},
             "metadata": {"asset": asset, "symbol": "{}-USD".format(asset)}
             })
        crypto_collection = []
        for col in collection:
            crypto_collection.append(CollectionType(time=col["ts"], price=col["price"]))
        return crypto_collection

