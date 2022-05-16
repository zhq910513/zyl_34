#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_list.py
@time: 2022/4/21 14:17
"""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import copy
from common.log_out import log_err, log
from dbs.pipelines import MongoPipeline

requests.packages.urllib3.disable_warnings()


# 请求列表
def product_list(company_info):
    try:
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
    soup = BeautifulSoup(html, 'lxml')
    domain = urlparse(company_info['产品链接']).netloc
    print(domain)

    try:
        if domain == "www.1688.com":
            for pro in soup.find_all('li', {'class': 'sm-offer-item sw-dpl-offer-item'}):
                pro_name = pro.find_all('a')[0].get('title')
                pro_link = pro.find_all('a')[0].get('href')
                if str(pro_link).startswith('//'):
                    pro_link = 'https:' + pro_link
                pro_data = {
                    '机构简称': company_info['机构简称'],
                    '企业类型': company_info['企业类型'],
                    '企业动态': company_info.get('企业动态'),
                    '产品链接': company_info['产品链接'],
                    'domain': domain,
                    'pro_name': pro_name,
                    'pro_link': pro_link
                }
                # print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
    except Exception as error:
        log_err(error)


if __name__ == "__main__":
    company_dict = {
        '机构简称': '巷口塑胶',
        '企业类型': '制品厂',
        '企业动态': '',
        '产品链接': 'https://www.1688.com/store/80707D7367D7C6955BAB81A659B3E1BB.html'
    }
    product_list(company_dict)
