#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_list.py
@time: 2022/4/21 14:17
"""
import json
from urllib.parse import urlparse,urlencode

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err
from dbs.pipelines import MongoPipeline

requests.packages.urllib3.disable_warnings()


# 请求列表
def product_list(company_info):
    try:
        if 'zzxksj.1688.com' in company_info['产品链接']:
            parse_list(company_info, '')
        else:
            headers = {
                'authority': 'www.1688.com',
                'method': 'GET',
                'scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
            }
            resp = requests.get(company_info['产品链接'], headers=headers, verify=False)
            resp.encoding = 'gbk'
            if resp.status_code == 200:
                parse_list(company_info, resp.text)
            else:
                print(resp.status_code)
    except Exception as error:
        log_err(error)


# 解析列表
def parse_list(company_info, html):
    if html:
        soup = BeautifulSoup(html, 'lxml')
    domain = urlparse(company_info['产品链接']).netloc
    print(domain)

    try:
        if domain == "zzxksj.1688.com":
            jsonData = json.load(open(f'D:\Projects\dev\zyl_34\spiders\data.json','r',encoding="utf-8"))
            for item in jsonData.get('data').get('content').get('offerList'):
                pro_name = item.get('subject')
                pro_link = f"https://detail.1688.com/offer/{item.get('id')}.html"
                pro_data = {
                    '机构简称': company_info['机构简称'],
                    '企业类型': company_info['企业类型'],
                    '企业动态': company_info.get('企业动态'),
                    '产品链接': company_info['产品链接'],
                    'domain': 'detail.1688.com',
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
    except Exception as error:
        log_err(error)
