import json
from MongoConnector import MongoConnector
import threading
from datetime import datetime, timezone, timedelta
from CollectionType import CollectionType

class Crypto():
    def __init__(self, asset, quantity):
        self.asset = asset
        self.quantity = quantity
        self.collections = []
        self.collection_min_price = None
        self.collection_max_price = None
        self.collection_avr_prices_in_hours = []
        self.collection_prices_diff_in_hours = []
        self.collection_prices_diff_perc = []
        self.last_price = None
        self.first_price = None
        self.diff_inn_24_hours_perc = None

class DataAnalysis():
    def __init__(self, assets, mongoClient):
        # crypto listesi
        self.mongoClient = mongoClient
        self.my_cryptos = []
        self.my_cryptos_usd_worth = Crypto("total", 0)
        self.my_assets = assets
        self.max_increased_perc_in_24_hours = 0
        self.max_decreased_perc_in_24_hours = 0

    def analysis_process(self):
        print("analysis_process giris")
        # Crypto listesi yaratılır
        self.create_crypto_list()
        # Crypto ların son 24 saatlik verisi çekilir
        self.get_crypto_collection_last_hours(24)
        # Crypto ların toplam USD değerleri hesaplanır
        self.calculate_cryptos_total_worth()
        # Crypto lar için min ve max tutarlar bulunur
        self.find_out_min_max_prices()
        # Crypto lar için Son 24 saat içindeki saatlik ortalama değerleri bulunur
        self.find_avarage_prices_in_hours()
        # Crypto lar için Son 24 saat içindeki saatlik ortalama değer farkları bulunur
        self.find_avarage_prices_diff_in_hours()
        # İzlenen crypto varlıkları mongo db ye yazılır
        self.add_assets_info_to_monge_db()


    def add_assets_info_to_monge_db(self):
        asset_list = []
        for crypto in self.my_cryptos:
            asset_list.append({
                "asset": crypto.asset,
                "quantity": crypto.quantity,
                "worth": crypto.last_price * crypto.quantity,
                "last_price": crypto.last_price,
                "is_most_increased": self.max_increased_perc_in_24_hours == crypto.diff_inn_24_hours_perc,
                "is_most_decreased": self.max_decreased_perc_in_24_hours == crypto.diff_inn_24_hours_perc
            })
        self.mongoClient.add_assets(asset_list)

    def calculate_cryptos_total_worth(self):
        for ind in range(len(self.my_cryptos[0].collections)):
            total_price = 0
            for crypto in self.my_cryptos:
                total_price += crypto.collections[ind].price * crypto.quantity
            collection_type = CollectionType(time=self.my_cryptos[0].collections[ind].time, price=total_price)
            self.my_cryptos_usd_worth.collections.append(collection_type)
        # for col in self.my_cryptos_usd_worth.collections:
        #     print("total_usd: ", col.time, col.price)

    def find_avarage_prices_diff_in_hours(self):
        for crypto in self.my_cryptos:
            diffrences = []
            print("avarage prices diffrences: ", crypto.asset)
            avr_prices = crypto.collection_avr_prices_in_hours
            for ind in range(len(avr_prices)-1):
                diff = avr_prices[ind+1] - avr_prices[ind]
                diffrences.append(diff)
                diff_perc = 0 if avr_prices[ind] == 0 else diff / avr_prices[ind] * 100
                crypto.collection_prices_diff_perc.append(diff_perc)
            crypto.collection_prices_diff_in_hours = diffrences
            # for col in crypto.collection_prices_diff_in_hours:
            #     print(crypto.asset, " diff: ", col)
            # for col in crypto.collection_prices_diff_perc:
            #     print(crypto.asset, " diff_perc: ", col)


    def find_avarage_prices_in_hours(self):
        for crypto in self.my_cryptos:
            for hour in range(24):
                total = 0
                count = 0
                search_start_time = self.add_hours_to_now(hours=-24+hour)
                search_end_time = self.add_hours_to_now(hours=-24+hour+1)

                for col in crypto.collections:
                    if search_start_time <= col.time < search_end_time:
                        total += col.price
                        count += 1
                avr = 0 if count == 0 else total / count
                crypto.collection_avr_prices_in_hours.append(avr)
            print("avarage prices: ", crypto.asset)
            # for col in crypto.collection_avr_prices_in_hours:
            #     print(col)

    def add_hours_to_now(self, hours):
        return datetime.now() + timedelta(hours=hours)

    def create_crypto_list(self):
        for asset in self.my_assets:
            self.my_cryptos.append(Crypto(asset=asset[0], quantity=asset[1]))

    def get_crypto_collection_last_hours(self, hours):
        for crypto in self.my_cryptos:
            crypto.collections = self.mongoClient.get_crypto_data_by_asset_last_hours(asset=crypto.asset, hours=hours)
            if crypto.collections is not None and len(crypto.collections) > 0:
                crypto.last_price = crypto.collections[-1].price
                crypto.first_price = crypto.collections[0].price
                crypto.diff_inn_24_hours_perc = (crypto.last_price - crypto.first_price) / crypto.first_price * 100
                if crypto.diff_inn_24_hours_perc > self.max_increased_perc_in_24_hours:
                    self.max_increased_perc_in_24_hours = crypto.diff_inn_24_hours_perc
                if crypto.diff_inn_24_hours_perc < self.max_decreased_perc_in_24_hours:
                    self.max_decreased_perc_in_24_hours = crypto.diff_inn_24_hours_perc
                print("first", crypto.asset, crypto.first_price, crypto.collections[0].time, crypto.diff_inn_24_hours_perc)
                print("last", crypto.asset, crypto.last_price, crypto.collections[-1].time, crypto.diff_inn_24_hours_perc)
            # print(crypto.asset)
            # for col in crypto.collections:
            #     print(col.time, col.price)

    def find_out_min_max_prices(self):
        for crypto in self.my_cryptos:
            for col in crypto.collections:
                if crypto.collection_min_price is None:
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




