import json
from RestApi import RestApi, HttpMethode
from MongoConnector import MongoConnector
from crypto_analyzer import DataAnalysis
import threading
from datetime import datetime, timezone, timedelta

#Crypto Settings
# Cryptoları hangi borsadan takip edeceğim
exchange = "COINBASE"
#Crypto Settings
# İzlmek istediğim cryptolar
#             Varlık adı, Miktarı  Hedef Değer
my_assets = [["ETH",      0.8,     3805],
             ["BTC",      0.1,     59350],
             ["DOGE",     5000,    0.384],
             ["ATOM",     30,      43.8],
             ["FIL",      30,      90]]

#API Settings
CRYPTINGUP_URL_BASE = "https://www.cryptingup.com/api/"
cryptingup_api = RestApi(url_base=CRYPTINGUP_URL_BASE)
#Kac saniyede bir market datasının alınacağı ve datat analiz yapılacağı
data_collect_cycle_time_sec = 120
data_analysis_cycle_time_sec = 150

# Mongo client Oluşturulur
mongoClient = MongoConnector(db_name="crypto_db", host="mongodb://localhost:27017/")


class CryptoTracker(object):
    def __init__(self, assets):
        self.my_assets = assets

    def timer_data_collect_process(self):
        print("yigit timer_process giris")
        # Market datası okunur
        response = cryptingup_api.api_call(function="assets/USD/markets", httpMethode=HttpMethode.GET)
        # print(response)
        if response.status_code != 200:
            return
        # Market Datası
        response_json = json.loads(response.text)
        markets = response_json["markets"]
        # print("markets:", markets)

        asset_datas = []
        ts = datetime.now() + timedelta(hours=3)
        #Market datası içinde cyrptoları ara
        total_amount = 0
        for asset in my_assets:
            asset_name = asset[0]
            asset_data, price = self.find_asset_in_market(markets, asset_name, ts)
            total_amount += price * asset[1]
            print("asset_data:", asset_data)
            asset_datas.append(asset_data)

        #Cryptolar USD karşılıkları Mongo db ye yazılır
        mongoClient.add_cryptos(asset_datas)

        # Toplam varlık bilgisi mongodb ye gönderiliyor
        mongoClient.add_total_asset(self.get_total_asset_json(ts, total_amount))

        #Timer tekrar kurulur
        t = threading.Timer(data_collect_cycle_time_sec, self.timer_data_collect_process)
        t.start()

    def get_total_asset_json(self, time, total_price):
        return {
                "ts": time,
                "metadata": {"asset": "total_usd", "symbol": "worth-usd"},
                "price": total_price
        }

    def timer_crypto_analysis_process(self):
        dataAnalysis = DataAnalysis(assets=my_assets, mongoClient=mongoClient)
        dataAnalysis.analysis_process()
        # Timer tekrar kurulur
        z = threading.Timer(data_analysis_cycle_time_sec, self.timer_crypto_analysis_process)
        z.start()

    def find_asset_in_market(self, markets, asset, ts):
        for market in markets:
            if exchange == market["exchange_id"] and asset == market["base_asset"]:
                return (
                    {
                        "ts": ts,
                        "metadata": {"asset": asset, "symbol": market["symbol"]},
                        "price": market["price"]
                    },
                    market["price"]
                )


#Baslangic mongo db bağlantısı yapılır
db_result = mongoClient.connect()
if db_result:
    cryptoTracker = CryptoTracker(assets=my_assets)
    # Data Collector Timer başlatılır
    cryptoTracker.timer_data_collect_process()
    # Data Analyszer Timer başlatılır
    cryptoTracker.timer_crypto_analysis_process()



