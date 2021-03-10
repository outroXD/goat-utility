# -*- coding: utf-8 -*-

from enum import Enum


class Messages(Enum):
    HTTP_STATUS_ERROR = "通信エラーが発生した為、スクリプトを停止します。 STATUS_CODE:{}"
    LINE_NOTIFY = "前回資金調達レート: {}, 次回予測資金調達レート: {}"
