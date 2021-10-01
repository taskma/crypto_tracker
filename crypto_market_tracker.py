import json
from RestApi import RestApi, HttpMethode
from MongoConnector import MongoConnector
import threading
from datetime import datetime, timezone

#Crypto Settings
# Cryptoları hangi borsadan takip edeceğim
exchange = "COINBASE"
# İzlmek istediğim cryptolar
my_assets = ["ETH", "BTC", "DOGE", "ATOM", "FIL"]

#API Settings
CRYPTINGUP_URL_BASE = "https://www.cryptingup.com/api/"
cryptingup_api = RestApi(url_base=CRYPTINGUP_URL_BASE)
#Kac saniyede bir market datasının alınacağı
api_cycle_time_sec = 60

# Mongo client Oluşturulur
mongoClient = MongoConnector(db_name="crypto_db", collection_name="crypto_series2", host="mongodb://localhost:27017/")

class DataCollect():
    def __init__(self):
        pass

    def timer_process(self):
        mongoClient.findQuery()
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
            asset_data = self.find_asset_in_market(markets, asset, ts)
            print("asset_data:", asset_data)
            asset_datas.append(self.find_asset_in_market(markets, asset, ts))

        #Cryptolar USD karşılıkları Mongo db ye yazılır
        mongoClient.addDatas(asset_datas)

        #Timer tekrar kurulur
        t = threading.Timer(api_cycle_time_sec, self.timer_process)
        t.start()

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
    dataCollect = DataCollect()
    # Timer başlatılır
    dataCollect.timer_process()



