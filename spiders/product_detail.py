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
import pprint
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from main import chrome
from spiders.download import command_thread, format_img_url, serverUrl

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)


# 请求列表
def product_detail(product_info):
    try:
        if product_info['domain'] == 'detail.1688.com':
            headers = {
            'authority': 'detail.1688.com',
            'method': 'GET',
            'path': '/offer/648047141570.html',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'cookie': '_bl_uid=3Cl953y390Urn56d8y8v06vk4p3q; cna=v4lAGupGjjwCAXQYQ3wbPELx; xlly_s=1; lid=%E5%9F%83%E8%8F%B2%E5%B0%94xq; _csrf_token=1652773013272; cookie2=127780e170b62dfbfb51a81ba803414d; sgcookie=E100JzJbvIdWr38tSeJ5zUNSQOS9QJiFEbxT2AyhiaiDielZF0duuadOLjTjT3ySihnDC8gwlMygyBub%2B4U6b3QMnK054Kl0TLOgEmpn0VQuBrsN8mrGu2Wmh0WwkKDGtFKB; t=828934da56477500317ebf80872fbe23; _tb_token_=e7e6e6e8eb1e6; __cn_logon__=false; _m_h5_tk=9be840572cdeb3d0f7f00c3353dbba56_1652781606492; _m_h5_tk_enc=3bf6a4c3875dc4dacb20607fffae8e30; tfstk=cnf5BwXVW0mWU0yEaaa4TKxz2VARZF06R8tlPo9BTPcbOeQ5imcwfm_1KDdeJE1..; l=eBxjF-1VLK7sYiQsBOfwourza77OSIRAguPzaNbMiOCPseCW56C5W6fDQO8XC3GVh6mXR37GxW6JBeYBqQOSnxvOIKDjYDkmn; isg=BAYG5_i3mJIVDEz2GzDMZAEyV_yIZ0oh2r9UBvAv8ikE86YNWPeaMeyDzy8_20I5',
            'pragma': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
        }
        else:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
            }
        print(product_info['pro_link'])
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
    soup = BeautifulSoup(html, 'lxml')
    if product_info['domain'] == 'detail.1688.com':
        driver = chrome()
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

            try:
                driver.get(product_info['pro_link'])
                time.sleep(1)
                html = driver.page_source
                chrome_soup = BeautifulSoup(html, 'lxml')
                pro_detail_html = chrome_soup.find('div', {'class': 'content-detail'})
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                info = re.findall('window.__INIT_DATA=(.*?)\n?  ?</script>', str(html), re.S)
                if info:
                    for key, value in json.loads(info[0]).get('data').items():
                        if value.get('componentType') == '@ali/tdmod-od-gyp-pc-main-pic':
                            for img_url in value.get('data').get('offerImgList'):
                                new_img_url = format_img_url(product_info, img_url)
                                if not new_img_url: continue
                                if new_img_url and new_img_url not in pro_images_front:
                                    replace_list.append(img_url)
                                    pro_images_front.append(new_img_url)

                # 替换非产品图片
                not_pro_pic_list = [img.get('src') for img in pro_detail_html.find_all('img')]
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if not new_img_url: continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_detail_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_detail_html = str(pro_detail_html).replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_detail_html = pro_detail_html.replace('\n',"").replace('\t',"").replace('\r',"").replace('\"',"'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_td': pro_td,
                'pro_detail_html': pro_detail_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            MongoPipeline('products').update_item({'pro_link': None}, _data)
            shutil.rmtree(f"D:/Projects/dev/zyl_34/download_data/{product_info['机构简称']}", True)
        except Exception as error:
            log_err(error)
        finally:
            driver.close()

    if product_info['domain'] == 'www.zzmushroom.com':
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

            try:
                pro_detail_html = soup.find('div', {'class': 'content-detail'})
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                info = re.findall('window.__INIT_DATA=(.*?)\n?  ?</script>', str(html), re.S)
                if info:
                    for key, value in json.loads(info[0]).get('data').items():
                        if value.get('componentType') == '@ali/tdmod-od-gyp-pc-main-pic':
                            for img_url in value.get('data').get('offerImgList'):
                                new_img_url = format_img_url(product_info, img_url)
                                if not new_img_url: continue
                                if new_img_url and new_img_url not in pro_images_front:
                                    replace_list.append(img_url)
                                    pro_images_front.append(new_img_url)

                # 替换非产品图片
                not_pro_pic_list = [img.get('src') for img in pro_detail_html.find_all('img')]
                if not_pro_pic_list:
                    for img_url in not_pro_pic_list:
                        new_img_url = format_img_url(product_info, img_url)
                        if not new_img_url: continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)), Async=True)

                # 替换产品图片
                if pro_detail_html and replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_detail_html = str(pro_detail_html).replace(img_url, new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_detail_html = pro_detail_html.replace('\n',"").replace('\t',"").replace('\r',"").replace('\"',"'")

            _data = {
                'pro_link': product_info['pro_link'],
                'pro_td': pro_td,
                'pro_detail_html': pro_detail_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            MongoPipeline('products').update_item({'pro_link': None}, _data)
            shutil.rmtree(f"D:/Projects/dev/zyl_34/download_data/{product_info['机构简称']}", True)
        except Exception as error:
            log_err(error)
