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
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, format_img_url, serverUrl

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)


def chrome():
    chrome_options = Options()
    # 去除webdriver和自动测试提示,增加无头
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chromedriver = webdriver.Chrome(options=chrome_options,
                                    executable_path=r"C:\Users\65769\AppData\Local\Programs\Python\Python38\chromedriver")
    chromedriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """
    })
    return chromedriver


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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
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
                pro_yy = None
            except:
                pro_yy = None

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

                # 产品图
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

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
        finally:
            driver.close()
    if product_info['domain'] == 'www.zzmushroom.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'productDetail'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'content'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'productDetail'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # print(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fjxhsj.com':
        try:
            try:
                pro_yy = soup.find('ol', {
                    'class': 'am-breadcrumb am-breadcrumb-slash am-animation-slide-top am-animation-delay-1'}).find_all(
                    'li')[2].get_text()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(
                    soup.find('div', {'class': 'pro_intro am-animation-slide-bottom am-animation-delay-2'}).find('div',
                                                                                                                 {
                                                                                                                     'id': 'con_one_1'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div',
                                     {'class': 'pro_show am-animation-slide-bottom am-animation-delay-1'}).find_all(
                        'img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'pro_intro am-animation-slide-bottom am-animation-delay-2'}).find(
                        'div', {'id': 'con_one_1'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.youyitape.com':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'view-nav'}).find_all('a')[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'detail-t1'}).get_text().replace('\n', '').replace('\t',
                                                                                                       '').replace('\r',
                                                                                                                   '').strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'detail_title2 mhide'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'img-dv'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'detail_title2 mhide'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.tjhybz.com':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'neititle'}).find('h2').get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'content'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'main_right fr'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'content'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.guanyipipe.com": pass
    if product_info['domain'] == 'www.minqiao.com.cn':
        try:
            try:
                pro_yy = soup.find('span', {'class': 'hidden-xs link'}).find_all('a')[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'info-content'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'info-pic'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'info-content'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.ruihua650.com": pass
    if product_info['domain'] == 'www.innovapack.com.cn':
        try:
            try:
                pro_yy = '-'.join(
                    soup.find('div', {'class': 'w-crumbs'}).get_text().strip().replace('\n', '').replace('\xa0',
                                                                                                         '').replace(
                        '首页ꄲ', '').split('ꄲ'))
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = None
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find_all('img', {'class': 'CutFill'}):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.st-gh.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = []
                for p in soup.find('div', {'class': 'reset_style js-reset_style js-adapMobile'}).find_all('p')[1:]:
                    if p.get_text():
                        pro_td.append(p.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip())
                if pro_td:
                    pro_td = ' '.join(pro_td).strip()
                else:
                    pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'reset_style js-reset_style js-adapMobile'}).find('p',
                                                                                                                   {
                                                                                                                       'style': 'text-align: center;'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                imgs = re.findall('"srcBigPic":"(.*?)"', html, re.S)
                if imgs:
                    for img_url in imgs:
                        new_img_url = format_img_url(product_info, img_url)
                        if not new_img_url: continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fjxl.com':
        try:
            try:
                pro_yy = soup.find('ul', {'class': 'product-detail-item'}).find_all('li')[0].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('ul', {'class': 'xypg-left-nav'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'product-detail-swiper'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fzlvfan.com':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'nyright_bt'}).get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = []
                for span in soup.find('div', {'class': 'cenn'}).find_all('span')[1:]:
                    pro_detail_html.append(str(span))
                if pro_detail_html:
                    pro_detail_html = '\n'.join(pro_detail_html)
                else:
                    pro_detail_html = str(soup.find('div', {'class': 'nyright_bt'}).find_next('div'))
            except:
                pro_detail_html = None

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.amesonpak.com':
        try:
            try:
                pro_yy = soup.find('h3', {'class': 'fl'}).get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'prod-detRi-desc'}).get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'contain-box'}).find_next('div'))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'pro-zoom'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'class': 'contain-box'}).find_next('div').find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.atontech.com.cn':
        try:
            try:
                pro_yy = []
                for a in soup.find('div', {'class': 'bread'}).find_all('a')[1:]:
                    pro_yy.append(a.get_text().strip())
                if pro_yy:
                    pro_yy = '-'.join(pro_yy)
                else:
                    pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'ms_rfont'}).get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'id': 'xq'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'left-pro'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if str(new_img_url).endswith('.gif'): continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 替换非产品图片
                for img in soup.find('div', {'id': 'xq'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if str(new_img_url).endswith('.gif'): continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.kaidapack.com": pass
    if product_info['domain'] == 'www.fjzhongya.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = None
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'productimg'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                        hash_key = hashlib.md5(new_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fzghxc.com':
        try:
            try:
                pro_yy = soup.find_all('div', {'class': 'e_breadcrumb e_breadcrumb-001 p_breadcrumb'})[-1].find(
                    'span').get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = ''
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                imgs = re.findall('"srcBigPic":"(.*?)"', str(html), re.S)
                if imgs:
                    for img_url in imgs:
                        new_img_url = format_img_url(product_info, img_url)
                        if not new_img_url: continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                            hash_key = hashlib.md5(new_img_url.encode("utf8")).hexdigest()
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)
                            pro_detail_html = str(pro_detail_html).replace(img_url, new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)), Async=True)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'xm-devon.com':
        try:
            try:
                pro_detail_html = str(soup.find_all('div', {'class': 'wp-media_content'})[1])
                if pro_detail_html:
                    pro_detail_html = product_info['产品详情'] + '\n' + pro_detail_html
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 替换非产品图片
                for img in soup.find_all('div', {'class': 'wp-media_content'})[1].find_all('img'):
                    img_url = img.get('data-original')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if str(new_img_url).endswith('.gif'): continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                if pro_images_front:
                    pro_images_front = product_info['pro_images_front'] + pro_images_front
                if pro_images_back:
                    pro_images_back = product_info['pro_images_back'] + pro_images_back
            except:
                pro_images_front = None
                pro_images_back = None
            finally:
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品详情': pro_detail_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == "www.zpwpw.cn": pass
    if product_info['domain'] == 'www.jinguan-cn.com':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'w-breadcrumbs'}).find_all('a')[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = ''
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'product-detail-images'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                        hash_key = hashlib.md5(new_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
                        pro_detail_html = str(pro_detail_html).replace(img_url, new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)), Async=True)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.gdyuanchengsy.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('span', {'class': 'cpxqbox_nr'}).find_next('div'))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('span', {'class': 'cpxqbox_nr'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.leyouguandao.com':
        try:
            try:
                pro_yy = soup.find_all('div', {'class': 'nav_tit'})[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = []
                for p in soup.find('div', {'class': 'pro_info'}).find('div', {'class': 'fr'}).find_all('p')[1:]:
                    text = p.get_text()
                    if text:
                        pro_td.append(text)
                if pro_td:
                    pro_td = '\n'.join(pro_td)
                else:
                    pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'pro_desc_main'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'img_list'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 非产品图
                for img in soup.find('div', {'class': 'pro_desc_main'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.pvc123.com':
        try:
            try:
                pro_yy = None
                for td in soup.find_all('td', {'class': 'f_dblue'}):
                    if '产品/服务' in str(td):
                        td_content = td.find_next('td')
                        pro_yy = td_content.find('strong').get_text()
            except:
                pro_yy = None

            try:
                pro_td = None
                if soup.find_all('div', {'class': 'main_head'}):
                    for num, head in enumerate(soup.find_all('div', {'class': 'main_head'})):
                        try:
                            if '产品优势' in head.get_text():
                                content = soup.find_all('div', {'class': 'main_body'})[num]
                                pro_td = content.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                        '').strip()
                        except:
                            pass
            except:
                pro_td = None

            try:
                pro_detail_html = None
                if soup.find_all('div', {'class': 'main_head'}):
                    for num, head in enumerate(soup.find_all('div', {'class': 'main_head'})):
                        try:
                            if '详细信息' in head.get_text():
                                pro_detail_html = soup.find_all('div', {'class': 'main_body'})[num]
                        except:
                            pass
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find_all('div', {'class': 'main_body'})[0].find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if str(new_img_url).endswith('.gif'): continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 非产品图
                if pro_detail_html:
                    for img in pro_detail_html.find_all('img'):
                        img_url = img.get('src')
                        new_img_url = format_img_url(product_info, img_url)
                        if not new_img_url: continue
                        if str(new_img_url).endswith('.gif'): continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                    pro_detail_html = str(pro_detail_html)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fjhoutiankeji.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'products_middle'}).find('p').get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'in_cont'}).find_all('p')[-1]) + '\n' + '\n'.join([str(i) for i in soup.find('div', {'class': 'in_cont'}).find_all('li')])
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'main_r_mid'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.dehanguan.com':
        try:
            try:
                pro_td = soup.find('div', {'class': 'wp-products-artview_info desc'}).find_all('p')[0].get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'wp-products-detail-desc detail'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'wp-new-prodcuts-detail'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'qzhhwfb.com':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'w-breadcrumbs'}).find_all('a')[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'prd_detInfo_con'}).get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'descon_item'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'product-detail-images'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 非产品图
                for img in soup.find('div', {'class': 'descon_item'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'msxbz.cn':
        try:
            try:
                pro_yy = '包装材料'
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'descon_item'}))
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'product-detail-images'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 非产品图
                for img in soup.find('div', {'class': 'descon_item'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.qzjtsj.cn':
        try:
            try:
                pro_yy = soup.find('div', {'class': 'model_dec_adress'}).find_all('a')[-1].get_text().strip()
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = None
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'model-dectil-img'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

                # 替换产品图片
                if replace_list:
                    for img_url in replace_list:
                        if 'zuiyouliao' in img_url: continue
                        encode_img_url = format_img_url(product_info, img_url)
                        if not encode_img_url: continue

                        hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                        new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                        pro_images_back.append(new_img_url)
            except:
                pro_images_front = None
                pro_images_back = None

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.fjlbgy.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = soup.find('div', {'class': 'col-xs-12'}).find_next('p').get_text().strip()
            except:
                pro_td = None

            try:
                pro_detail_html = []
                for p in soup.find('div', {'class': 'contentbox'}).find_all('p')[2:]:
                    pro_detail_html.append(str(p))
                if pro_detail_html:
                    pro_detail_html = '\n'.join(pro_detail_html)
                else:
                    pro_detail_html = ''
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'contentbox'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.chinatkp.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = str(soup.find('div', {'class': 'content'}).find_all('div')[-1])
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'content'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'www.jjxingtai.com':
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

            try:
                pro_td = None
            except:
                pro_td = None

            try:
                pro_detail_html = None
            except:
                pro_detail_html = None

            try:
                replace_list = []
                pro_images_front = []
                pro_images_back = []

                # 产品图
                for img in soup.find('div', {'class': 'prod-text10 text news-text3'}).find_all('img'):
                    img_url = img.get('src')
                    new_img_url = format_img_url(product_info, img_url)
                    if not new_img_url: continue
                    if new_img_url and new_img_url not in pro_images_front:
                        replace_list.append(img_url)
                        pro_images_front.append(new_img_url)

                # 下载
                if pro_images_front:
                    command_thread(product_info['机构简称'], list(set(pro_images_front)))

                # 替换产品图片
                if replace_list:
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

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            # pp.pprint(_data)
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
    if product_info['domain'] == 'lvshengpapercup.1688.com':
        driver = chrome()
        try:
            try:
                pro_yy = None
            except:
                pro_yy = None

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

                # 产品图
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

                # 下载
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
                pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r', "").replace('\"',
                                                                                                                "'")

            _data = {
                'pro_link': product_info['pro_link'],
                '产品特点': pro_td,
                '产品详情': pro_detail_html,
                '应用行业': pro_yy,
                'pro_images_front': pro_images_front,
                'pro_images_back': pro_images_back,
                'status': 1
            }
            MongoPipeline('products').update_item({'pro_link': None}, _data)
        except Exception as error:
            log_err(error)
        finally:
            driver.close()