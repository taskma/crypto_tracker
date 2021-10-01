import json
from enum import Enum
import requests

headers = {
    "Content-Type": "application/json"
}

class HttpMethode(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"

class RestApi(object):
    def __init__(self, url_base):
        self.url_base = url_base

    def api_call(self, function,  httpMethode, data=None, params={}):
        print("api_call giris")

        print(str(httpMethode), self.url_base + function, params)
        print("data", data)

        if httpMethode == HttpMethode.POST:
            response = requests.post(self.url_base + function,
                                     params=params, headers=headers, data=data)
        elif httpMethode == HttpMethode.GET:
            response = requests.get(self.url_base + function,
                                    params=params, headers=headers, data=data)
        elif httpMethode == HttpMethode.DELETE:
            response = requests.delete(self.url_base + function,
                                       params=params, headers=headers, data=data)

        if response.status_code != 200:
            print("Api hata döndü !!")
        print("response.json: ", response.json)
        print("response.text: ", response.text)
        return response

