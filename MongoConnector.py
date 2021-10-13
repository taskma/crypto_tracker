import json
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from CollectionType import CollectionType

class MongoConnector(object):
    def __init__(self, db_name, host):
        self.host = host
        self.db_name = db_name
        self.conn = None
        self.collection = None
        self.asset_col = None
        self.alarm_info = None
        self.db = None
        self.most_decreased_asset_moments = None
        self.most_fluctuationed_asset_moments = None

    def connect(self):
        try:
            conn = MongoClient(self.host)
            self.db = conn[self.db_name]
            self.collection = self.db["crypto_series2"]
            self.asset_col = self.db["assets"]
            self.alarm_info = self.db["alarm_info"]
            self.most_decreased_asset_moments = self.db["most_decreased_moments"]
            self.most_fluctuationed_asset_moments = self.db["most_fluctuationed_asset_moments"]
        except:
            print("MongoDB bağlanılamadı")
            return False
        print("MongoDB bağlantısı başarılı!!!")
        return True

    def add_most_decreased_asset_moments(self, data):
        self.most_decreased_asset_moments.drop()
        if data is not None and len(data) > 0:
            rec_id1 = self.most_decreased_asset_moments.insert_many(data)
            print("Data inserted with record ids", rec_id1)

    def add_most_fluctuationed_asset_moments(self, data):
        self.most_fluctuationed_asset_moments.drop()
        if data is not None and len(data) > 0:
            rec_id1 = self.most_fluctuationed_asset_moments.insert_many(data)
            print("Data inserted with record ids", rec_id1)

    def add_cryptos(self, data):
        # Insert Data
        rec_id1 = self.collection.insert_many(data)
        print("Data inserted with record ids", rec_id1)

    def add_assets(self, data):
        # print("data:", data)
        self.asset_col.drop()
        rec_id1 = self.asset_col.insert_many(data)
        print("Data inserted with record ids", rec_id1)

    def add_total_asset(self, data):
        rec_id1 = self.collection.insert_one(data)
        print("Data inserted with record ids", rec_id1)

    def add_alarm_info(self, data):
        self.alarm_info.drop()
        rec_id1 = self.alarm_info.insert_one(data)
        print("Data inserted with record ids", rec_id1)

    def get_crypto_data_by_asset_last_hours(self, asset, hours):
        search_time = datetime.now() + timedelta(hours=-1 * hours)
        collection = self.collection.find(
            {"ts": {"$gt": search_time},
             "metadata": {"asset": asset, "symbol": "{}-USD".format(asset)}
             }).sort("ts", 1)
        crypto_collection = []
        for col in collection:
            crypto_collection.append(CollectionType(time=col["ts"], price=col["price"]))
        return crypto_collection

