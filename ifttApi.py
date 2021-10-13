import json
from enum import Enum
import logging
import requests
import datetime

API_URL = "https://maker.ifttt.com/trigger/{}/with/key/{}"

class IFTTApi(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def sendWebHook(self, event_key, value1, value2 = "", value3 = ""):
        url = API_URL.format(event_key, self.api_key)
        data = {'value1': value1, 'value2': value2, 'value3': value3, }

        response = requests.post(url, data = data)
        print(response.text)
        if response.status_code != 200:
            print("iftt something went wrong")
        else:
            print("iftt succeed")
        return response.status_code, response.text
