# -*- coding: utf-8 -*-

# ------------------------------
# @Time    : 2023/6/26
# @Author  : gao
# @File    : ask_bid.py
# @Project : AmazingQuant
# ------------------------------
import os
import time, datetime
import threading
import queue

import numpy as np
import pandas as pd
import tgw

from AmazingQuant.data_center.tgw_source.tgw_api import TgwApiData
from AmazingQuant.data_center.tgw_source.tgw_login import tgw_login

security_code_list = []
market_type_list = []

zhangfu_dict = {}
price_spread_dict = {}
volume_spread_dict = {}


# 实现推送回调
class DataHandler(tgw.IPushSpi):
    def __init__(self) -> None:
        super().__init__()
        self.stock_data_queue = queue.Queue()
        for i in range(4):
            self.thread = threading.Thread(target=self.process_stock_data)
            self.thread.start()

        self.index_data_queue = queue.Queue()
        for i in range(8):
            self.thread_queue = threading.Thread(target=self.process_index_data)
            self.thread_queue.start()

    def process_index_data(self):
        while True:
            if not self.index_data_queue.empty():
                index_data = self.index_data_queue.get()
                index_data_queue = index_data.copy()
                print('security_code:', index_data_queue[0]['security_code'])
                print('market_type:', index_data_queue[0]['market_type'])

    def process_stock_data(self):
        while True:
            if not self.stock_data_queue.empty():
                data = self.stock_data_queue.get()
                data_queue = data.copy()
                # print('security_code', data_queue)
                global security_code_list
                global market_type_list
                if data_queue[0]['security_code'] not in security_code_list:
                    security_code_list.append(data_queue[0]['security_code'])

                if data_queue[0]['market_type'] not in market_type_list:
                    market_type_list.append(data_queue[0]['market_type'])

                print('security_code:', len(security_code_list))

                global zhangfu_dict
                if data_queue[0]['pre_close_price'] > 0:
                    zhangfu_dict[data_queue[0]['security_code']] = (data_queue[0]['last_price'] / data_queue[0][
                        'pre_close_price'] - 1) * 100
                else:
                    zhangfu_dict[data_queue[0]['security_code']] = np.nan
                global price_spread_dict
                price_spread_dict[data_queue[0]['security_code']] = (data_queue[0]['offer_price1'] - data_queue[0][
                    'bid_price1']) / 1000000

                global volume_spread_dict
                bid_volume_total = data_queue[0]['bid_volume1'] + data_queue[0]['bid_volume2'] + data_queue[0][
                    'bid_volume3'] + \
                                   data_queue[0]['bid_volume4'] + data_queue[0]['bid_volume5']
                offer_volume_total = data_queue[0]['offer_volume1'] + data_queue[0]['offer_volume2'] + data_queue[0][
                    'offer_volume3'] + \
                                     data_queue[0]['offer_volume4'] + data_queue[0]['offer_volume5']
                if offer_volume_total > 0:
                    volume_spread_dict[data_queue[0]['security_code']] = (bid_volume_total - offer_volume_total) / \
                                                                         offer_volume_total
                else:
                    volume_spread_dict[data_queue[0]['security_code']] = np.nan

    def OnMDSnapshot(self, data, err):
        if not data is None:
            self.stock_data_queue.put(data)
            pass
        else:
            print(err)

    def OnMDIndexSnapshot(self, data, err):
        if not data is None:
            self.index_data_queue.put(data)
        else:
            print(err)


if __name__ == "__main__":
    tgw_login()
    g_is_running = True
    tgw_api_object = TgwApiData()

    # 订阅沪深股票的实时五档快照行情
    for market_type in [tgw.MarketType.kSZSE, tgw.MarketType.kSSE]:
        sub_item = tgw.SubscribeItem()
        sub_item.security_code = ''
        sub_item.flag = tgw.SubscribeDataType.kSnapshot
        sub_item.category_type = tgw.VarietyCategory.kStock
        sub_item.market = market_type
        # 订阅
        data_handler = DataHandler()
        data_handler.SetDfFormat(False)
        success = tgw.Subscribe(sub_item, data_handler)

    # 订阅沪深指数的实时五档快照行情
    for market_type in [tgw.MarketType.kSZSE, tgw.MarketType.kSSE]:
        sub_item = tgw.SubscribeItem()
        sub_item.security_code = ''
        sub_item.flag = tgw.SubscribeDataType.kIndexSnapshot
        sub_item.category_type = tgw.VarietyCategory.kIndex
        sub_item.market = market_type
        # 订阅
        data_handler = DataHandler()
        data_handler.SetDfFormat(False)
        success = tgw.Subscribe(sub_item, data_handler)

        if success != tgw.ErrorCode.kSuccess:
            print(tgw.GetErrorMsg(success))

    while True:
        try:
            if g_is_running != True:
                break
        except Exception as e:
            print(str(e))

