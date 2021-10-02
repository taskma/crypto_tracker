import json
from MongoConnector import MongoConnector
import threading
from datetime import datetime, timezone, timedelta
from CollectionType import CollectionType

#Crypto Settings
# İzlmek istediğim cryptolar
my_assets = ["ETH", "BTC", "DOGE", "ATOM", "FIL"]

class Crypto():
    def __init__(self, asset):
        self.asset = asset
        self.collections = []
        self.collection_min_price = None
        self.collection_max_price = None
        self.collection_avr_prices_in_hours = [CollectionType]

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
        self.get_crypto_collection_last_hours(24)
        # Crypto lar için min ve max tutarlar bulunur
        self.find_out_min_max_prices()
        # Crypto lar için Son 24 saat içindeki saatlik ortalama değerleri bulunur
        self.find_avarage_prices_in_hours()

    def find_avarage_prices_in_hours(self):
        for crypto in my_cryptos:
            for hour in range(24):
                total = 0
                count = 0
                search_start_time = self.add_hours_to_now(hours=-24+hour)
                search_end_time = self.add_hours_to_now(hours=-24+hour+1)
                # print("search_start_time", search_start_time)
                # print("search_end_time", search_end_time)
                for col in crypto.collections:
                    if search_start_time <= col.time < search_end_time:
                        total += col.price
                        count += 1
                avr = 0 if count == 0 else total / count
                crypto.collection_avr_prices_in_hours.append(avr)
            print(crypto.asset)
            for col in crypto.collection_avr_prices_in_hours:
                print(col)

    def add_hours_to_now(self, hours):
        return datetime.now() + timedelta(hours=hours)

    def create_crypto_list(self):
        for asset in my_assets:
            my_cryptos.append(Crypto(asset))

    def get_crypto_collection_last_hours(self, hours):
        for crypto in my_cryptos:
            crypto.collections = mongoClient.get_crypto_data_by_asset_last_hours(asset=crypto.asset, hours=hours)
            # print(crypto.asset)
            # for col in crypto.collections:
            #     print(col.time, col.price)

    def find_out_min_max_prices(self):
        for crypto in my_cryptos:
            for col in crypto.collections:
                if crypto.collection_min_price == None:
                    crypto.collection_min_price = col.price
                    crypto.collection_max_price = col.price
                else:
                    if col.price < crypto.collection_min_price:
                        crypto.collection_min_price = col.price
                    if col.price > crypto.collection_max_price:
                        crypto.collection_max_price = col.price
            print(crypto.asset)
            print("crypto.collection_max_price:", crypto.collection_max_price)
            print("crypto.collection_min_price", crypto.collection_min_price)

#Baslangic mongo db bağlantısı yapılır
db_result = mongoClient.connect()

if db_result:
    dataAnalysis = DataAnalysis()
    # Analiz İşlemleri
    dataAnalysis.analysis_process()



