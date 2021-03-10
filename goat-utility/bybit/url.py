# -*- coding: utf-8 -*-

from enum import Enum
import hmac


class BybitUrls(Enum):
    GET_THE_LAST_FUNDING_RATE = 'https://api.bybit.com/v2/public/funding/prev-funding-rate?api_key={}&symbol={}'
    PREDICTED_FUNDING_RATE_AND_MY_FUNDING_FEE = 'https://api.bybit.com/v2/private/funding/predicted-funding?api_key={}&symbol={}&timestamp={}&sign={}'


class LineUrls(Enum):
    LINE_API_URL = 'https://notify-api.line.me/api/notify'
