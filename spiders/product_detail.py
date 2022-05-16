#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_detail.py
@time: 2022/4/21 14:17
"""
import hashlib
import json
import re
import pprint
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, format_img_url, serverUrl
requests.packages.urllib3.disable_warnings()
pp=pprint.PrettyPrinter(indent=4)


# 请求列表
def product_detail(product_info):
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
        resp = requests.get(product_info['pro_link'], headers=headers, verify=False)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            parse_detail(product_info, resp.text)
        else:
            print(resp.status_code)
    except Exception as error:
        log_err(error)

# 解析详细内容
def parse_detail(product_info, html):
    if product_info['domain'] == 'www.1688.com':
        try:
            try:
                pro_td = {}
                info = re.findall('window.__INIT_DATA=(.*?)\n?  ?</script>', str(html), re.S)
                if info:
                    for key, value in json.loads(info[0]).get('data').items():
                        if value.get('componentType') == '@ali/tdmod-od-pc-attribute-new':
                            for msg in value.get('data'):
                                name = msg.get('name')
                                value = msg.get('values')
                                if isinstance(value, list):
                                    value = ' | '.join(value)
                                pro_td.update({name: value})
            except:
                pro_td = None

            # try:
            #     pro_jscs_html = str(soup.find('div', {'class': 'show_property'})) + '\n' + str(
            #         soup.find('div', {'class': 'content_body'}))
            # except:
            #     pro_jscs_html = None
            #
            # try:
            #     replace_list = []
            #     pro_images_front = []
            #     pro_images_back = []
            #
            #     for img in soup.find('div', {'class': 'show_gallery'}).find_all('img'):
            #         try:
            #             img_url = img.get('src')
            #             if not isinstance(img_url, str): continue
            #
            #             new_img_url = format_img_url(product_info, img_url)
            #             if new_img_url and new_img_url not in pro_images_front:
            #                 replace_list.append(img_url)
            #                 pro_images_front.append(new_img_url)
            #         except:
            #             pass
            #
            #     # 替换非产品图片
            #     not_pro_pic_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
            #     if not_pro_pic_list:
            #         for img_url in not_pro_pic_list:
            #             new_img_url = format_img_url(product_info, img_url)
            #             if new_img_url and new_img_url not in pro_images_front:
            #                 replace_list.append(img_url)
            #                 pro_images_front.append(new_img_url)
            #
            #     if pro_images_front:
            #         command_thread(product_info['company_name'], list(set(pro_images_front)), Async=True)
            #
            #     # 替换产品图片
            #     if pro_jscs_html and replace_list:
            #         for img_url in replace_list:
            #             if 'zuiyouliao' in img_url: continue
            #             encode_img_url = format_img_url(product_info, img_url)
            #             if not encode_img_url: continue
            #
            #             hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
            #             new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
            #             pro_images_back.append(new_img_url)
            #             pro_jscs_html = pro_jscs_html.replace(img_url, new_img_url)
            # except:
            #     pro_images_front = None
            #     pro_images_back = None
            # finally:
            #     pro_jscs_html = pro_jscs_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"', "'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_td': pro_td,
                # 'pro_jscs_html': pro_jscs_html,
                # 'pro_images_front': pro_images_front,
                # 'pro_images_back': pro_images_back,
                # 'status': 1
            }
            pp.pprint(_data)
        except Exception as error:
            log_err(error)

if __name__ == "__main__":
    for pro_info in MongoPipeline('products').find({'status': None}):
        product_detail(pro_info)
        break