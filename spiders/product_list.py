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
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
            }
            resp = requests.get(company_info['产品链接'], headers=headers, verify=False)
            resp.encoding = 'utf-8'
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
        if domain == "zzxksj.1688.com":
            jsonData = json.load(open(f'D:\Projects\dev\zyl_34\spiders\data.json','r',encoding="utf-8"))
            for item in jsonData.get('data').get('content').get('offerList'):
                pro_name = item.get('subject')
                pro_link = f"https://detail.1688.com/offer/{item.get('id')}.html"
                pro_data = {
                    'pro_link': pro_link,
                    'domain': domain,
                    '机构简称': company_info['机构简称'],
                    '企业类型': company_info['企业类型'],
                    '企业动态': company_info.get('企业动态'),
                    '产品链接': company_info['产品链接'],
                    '产品名称': pro_name
                }
                # print(pro_data)
                MongoPipeline('products').update_item({'pro_link': None}, pro_data)
        if domain == "www.zzmushroom.com":
            try:
                for item in soup.find_all('div', {'class': 'pic fl'}):
                    pro_name = item.find_all('a')[-1].get('title')
                    pro_link = item.find_all('a')[-1].get('href')
                    if str(pro_link).startswith('pro'):
                        pro_link = 'http://www.zzmushroom.com/' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)

            try:
                current_page = int(company_info['产品链接'].split('page=')[1])
                if int(current_page) < 7:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page+1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.fjxhsj.com":
            try:
                for item in soup.find('div', {'class': 'home_pro'}).find_all('li'):
                    pro_name = item.find('a').get('title').strip()
                    pro_link = item.find('a').get('href')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.fjxhsj.com' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)

            try:
                current_page = int(company_info['产品链接'].split('page=')[1])
                if int(current_page) < 25:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page+1}'
                    return product_list(company_info)
            except:
                pass
    except Exception as error:
        log_err(error)
