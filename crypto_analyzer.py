import json
from MongoConnector import MongoConnector
import threading
from datetime import datetime, timezone

#Crypto Settings
# İzlmek istediğim cryptolar
my_assets = ["ETH", "BTC", "DOGE", "ATOM", "FIL"]

class Crypto():
    def __init__(self, asset):
        self.asset = asset
        self.collections = []
        self.collection_min_price = None
        self.collection_max_price = None
        self.collection_avr_prices_in_hours = None

#crypto listesi
my_cryptos = []

# Mongo client Oluşturulur
mongoClient = MongoConnector(db_name="crypto_db", collection_name="crypto_series2", host="mongodb://localhost:27017/")

class DataAnalysis():
    def __init__(self):
        pass

    def analysis_process(self):
        # Crypto listesi yaratılır
        self.create_crypto_list()
        # Crypto ların son 24 saatlik verisi çekilir
        self.get_crypto_collection_in_24_hours()
        # Crypto lar için min ve max tutarlar bulunur
        self.find_out_min_max_prices()


    def create_crypto_list(self):
        for asset in my_assets:
            my_cryptos.append(Crypto(asset))

    def get_crypto_collection_in_24_hours(self):
        for crypto in my_cryptos:
            crypto.collections = mongoClient.get_crypto_data_by_asset_in_24_hours(crypto.asset)
            # print(crypto.asset)
            # for col in crypto.collections:
            #     print(col)

    def find_out_min_max_prices(self):
        for crypto in my_cryptos:
            for col in crypto.collections:
                if crypto.collection_min_price == None:
                    crypto.collection_min_price = col["price"]
                    crypto.collection_max_price = col["price"]
                else:
                    if col["price"] < crypto.collection_min_price:
                        crypto.collection_min_price = col["price"]
                    if col["price"] > crypto.collection_max_price:
                        crypto.collection_max_price = col["price"]
            print(crypto.asset)
            print("crypto.collection_max_price:", crypto.collection_max_price)
            print("crypto.collection_min_price", crypto.collection_min_price)


#Baslangic mongo db bağlantısı yapılır
db_result = mongoClient.connect()

if db_result:
    dataAnalysis = DataAnalysis()
    # Analiz İşlemleri
    dataAnalysis.analysis_process()



