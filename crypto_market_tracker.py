import json
from RestApi import RestApi, HttpMethode
from MongoConnector import MongoConnector
from crypto_analyzer import DataAnalysis
import threading
from datetime import datetime, timezone

#Crypto Settings
# Cryptoları hangi borsadan takip edeceğim
exchange = "COINBASE"
#Crypto Settings
# İzlmek istediğim cryptolar
#           varlık adı, miktarı
my_assets = [["ETH",  0.3],
             ["BTC",  0.1],
             ["DOGE", 500],
             ["ATOM",  10],
             ["FIL",   10]]

#API Settings
CRYPTINGUP_URL_BASE = "https://www.cryptingup.com/api/"
cryptingup_api = RestApi(url_base=CRYPTINGUP_URL_BASE)
#Kac saniyede bir market datasının alınacağı ve datat analiz yapılacağı
data_collect_cycle_time_sec = 120
data_analysis_cycle_time_sec = 150

# Mongo client Oluşturulur
mongoClient = MongoConnector(db_name="crypto_db", collection_name="crypto_series2", host="mongodb://localhost:27017/")


class CryptoTracker(object):
    def __init__(self, assets):
        self.my_assets = assets

    def timer_data_collect_process(self):
        print("yigit timer_process giris")
        # Market datası okunur
        response = cryptingup_api.api_call(function="assets/USD/markets", httpMethode=HttpMethode.GET)
        print(response)
        if response.status_code != 200:
            return
        # Market Datası
        response_json = json.loads(response.text)
        markets = response_json["markets"]
        print(type(markets))
        print("markets:", markets)

        asset_datas = []
        ts = datetime.now()
        #Market datası içinde cyrptoları ara
        for asset in my_assets:
            asset_name = asset[0]
            asset_data = self.find_asset_in_market(markets, asset_name, ts)
            print("asset_data:", asset_data)
            asset_datas.append(self.find_asset_in_market(markets, asset_name, ts))

        #Cryptolar USD karşılıkları Mongo db ye yazılır
        mongoClient.add_cryptos(asset_datas)

        #Timer tekrar kurulur
        t = threading.Timer(data_collect_cycle_time_sec, self.timer_data_collect_process)
        t.start()

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
                    }
                )


#Baslangic mongo db bağlantısı yapılır
db_result = mongoClient.connect()
if db_result:
    cryptoTracker = CryptoTracker(assets=my_assets)
    # Data Collector Timer başlatılır
    cryptoTracker.timer_data_collect_process()
    # Data Analyszer Timer başlatılır
    cryptoTracker.timer_crypto_analysis_process()



