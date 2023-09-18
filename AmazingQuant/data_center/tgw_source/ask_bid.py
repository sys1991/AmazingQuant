# -*- coding: utf-8 -*-

# ------------------------------
# @Time    : 2023/6/26
# @Author  : gao
# @File    : ask_bid.py 
# @Project : AmazingQuant 
# ------------------------------
import os
import time, datetime

import pandas as pd
import tgw


from AmazingQuant.data_center.tgw_source.tgw_api import TgwApiData
from AmazingQuant.data_center.tgw_source.tgw_login import tgw_login

security_code_list = []
market_type_list = []


# 实现推送回调
class DataHandler(tgw.IPushSpi):
    def __init__(self) -> None:
        super().__init__()

    def OnMDSnapshot(self, data, err):
        if not data is None:
            global security_code_list
            global market_type_list
            if data[0]['security_code'] not in security_code_list:
                security_code_list.append(data[0]['security_code'])
                print('security_code_list', len(security_code_list), data[0]['security_code'])

            if data[0]['market_type'] not in market_type_list:
                market_type_list.append(data[0]['market_type'])
                print('market_type_list', len(market_type_list))
            # if data[0]['security_code'] == '000002':
            #     print(data[0]['orig_time'], data[0]['last_price']/1000000)
            pass
        else:
            print(err)

    def OnMDIndexSnapshot(self, data, err):
        if not data is None:
            pass
        else:
            print(err)


if __name__ == "__main__":
    tgw_login()
    g_is_running = True
    tgw_api_object = TgwApiData(20991231)
    code_sh_list, code_sz_list = tgw_api_object.get_code_list()
    print(len(code_sh_list), len(code_sz_list))
    sub_item_list = []
    data_hander = DataHandler()
    data_hander.SetDfFormat(False)
    for code in code_sh_list:
        sub_item = tgw.SubscribeItem()
        sub_item.security_code = code
        sub_item.SubscribeDataType = tgw.SubscribeDataType.kSnapshot
        sub_item.VarietyCategory = tgw.VarietyCategory.kStock
        sub_item.market = tgw.MarketType.kSSE
        sub_item_list.append(sub_item)
    for code in code_sz_list:
        sub_item = tgw.SubscribeItem()
        sub_item.security_code = code
        sub_item.SubscribeDataType = tgw.SubscribeDataType.kSnapshot
        sub_item.VarietyCategory = tgw.VarietyCategory.kStock
        sub_item.market = tgw.MarketType.kSZSE
        sub_item_list.append(sub_item)

    success = tgw.Subscribe(sub_item_list,  data_hander)

    print('success', success)
    if success != tgw.ErrorCode.kSuccess:
        print(tgw.GetErrorMsg(success))
    while True:
        try:
            if g_is_running != True:
                break
        except Exception as e:
            print(str(e))
        time.sleep(1)
