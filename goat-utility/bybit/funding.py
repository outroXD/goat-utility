# -*- coding: utf-8 -*-

from dataclasses import dataclass
import configparser
import time
import urllib.request
import urllib.parse
from http import HTTPStatus
import json
import hmac
from typing import Union
from symbol import Symbols
from url import BybitUrls, LineUrls
from messages import Messages

# SETTINGS 実行時はここ設定して！
SLEEP_TIME = 3600  # 1時間


@dataclass
class ApiConfig:
    bybit_api_name: str
    bybit_api_secret: str
    bybit_secret_key: str
    line_token: str

    @classmethod
    def build(cls) -> 'ApiConfig':
        config = configparser.ConfigParser()
        config.read('../conf/conf.ini')
        bybit_api_name = config.get('bybit', 'API-NAME')
        bybit_api_secret = config.get('bybit', 'API-SECRET')
        bybit_secret_key = config.get('bybit', 'SECRET-KEY')
        line_token = config.get('LINE', 'TOKEN')
        return cls(bybit_api_name, bybit_api_secret, bybit_secret_key, line_token)


def send_message_to_line(message: str, config: ApiConfig) -> None:
    headers = {'Authorization': 'Bearer ' + config.line_token}
    data = {'message': message}
    payload = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(LineUrls.LINE_API_URL.value, data=payload, headers=headers, method='POST')
    with urllib.request.urlopen(request) as response:
        body = response.read()


def get_signature(api_secret: str, request_params: dict):
    _val = '&'.join([str(k) + "=" + str(v) for k, v in sorted(request_params.items()) if (k != 'sign') and (v is not None)])
    return str(hmac.new(bytes(api_secret, "utf-8"), bytes(_val, "utf-8"), digestmod="sha256").hexdigest())


if __name__ == '__main__':
    config: ApiConfig = ApiConfig.build()
    url_get_last_funding_rate: str = BybitUrls.GET_THE_LAST_FUNDING_RATE.value.format(config.bybit_api_secret, Symbols.BTCUSD.value)
    url_predicted_funding_rate_and_my_funding_fee: Union[str, None] = None
    url_line: str = LineUrls.LINE_API_URL.value

    while True:
        last_funding_rate: Union[str, None] = None
        with urllib.request.urlopen(url_get_last_funding_rate) as response:
            body = json.load(response)
            if body['ret_msg'] != HTTPStatus.OK.phrase:
                send_message_to_line(Messages.HTTP_STATUS_ERROR.value.format(body['ret_msg']), config)
                exit(1)
            last_funding_rate = body['result']['funding_rate']
            del body  # 一応、開放

        predicted_funding_rate: Union[str, None] = None
        timestamp: int = int(time.time() * 1000)
        signature: str = get_signature(config.bybit_secret_key, {'api_key': config.bybit_api_secret, 'symbol': Symbols.BTCUSD.value, 'timestamp': timestamp})
        url_predicted_funding_rate_and_my_funding_fee = \
            BybitUrls.PREDICTED_FUNDING_RATE_AND_MY_FUNDING_FEE.value.format(config.bybit_api_secret, Symbols.BTCUSD.value, timestamp, signature)
        with urllib.request.urlopen(url_predicted_funding_rate_and_my_funding_fee) as response:
            body = json.load(response)
            if body['ret_msg'] != HTTPStatus.OK.phrase:
                send_message_to_line(Messages.HTTP_STATUS_ERROR.value.format(body['ret_msg']), config)
                exit(1)
            print(body)
            predicted_funding_rate = str(body['result']['predicted_funding_rate'])
            del body  # 一応、開放

        message: str = Messages.LINE_NOTIFY.value.format(last_funding_rate, predicted_funding_rate)
        send_message_to_line(message, config)

        time.sleep(SLEEP_TIME)
