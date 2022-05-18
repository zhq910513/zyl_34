#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: the king
@project: zyl_company
@file: product_list.py
@time: 2022/4/21 14:17
"""
import hashlib
import json
import shutil
import time
from urllib.parse import urlparse,urlencode

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, serverUrl, format_img_url

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
        if domain == "www.youyitape.com":
            try:
                for item in soup.find_all('div', {'class': 'col-3'}):
                    pro_name = item.find('h3').get_text().strip()
                    pro_link = item.find('a').get('href')
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                if int(current_page) < 4:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page+1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.tjhybz.com":
            try:
                for item in soup.find('div', {'class': 'plist'}).find_all('li', {'class': 'fl'}):
                    pro_name = item.find('p').get_text().strip()
                    pro_link = item.find('a').get('href')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.tjhybz.com' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('/p/')[1].split('.')[0])
                if int(current_page) < 7:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.guanyipipe.com":
            try:
                for item in soup.find_all('div', {'class': 'swiper-slide'}):
                    try:
                        try:
                            pro_link = 'http://www.guanyipipe.com/' + item.find('img').get('src')
                        except:
                            pro_link = None

                        try:
                            pro_name = item.find('h4').get_text().strip()
                        except:
                            pro_name = None

                        try:
                            pro_yy = None
                        except:
                            pro_yy = None

                        try:
                            pro_td = []
                            for num, p in enumerate(item.find_all('p')):
                                if '产品特点' in str(p):
                                    for n_p in item.find_all('p')[num+1:]:
                                        pro_td.append(n_p.get_text().replace('\n', '').replace('\t', '').replace('\r', '').strip())
                                    break
                            if pro_td:
                                pro_td = '\n'.join(pro_td)
                            else:
                                pro_td = None
                        except:
                            pro_td = None

                        try:
                            pro_detail_html = str(item.find('em'))
                            if '产品简介' in str(item.find_all('p')[0]):
                                pro_detail_html = pro_detail_html + str(item.find_all('p')[0]) + str(item.find_all('p')[1])
                        except:
                            pro_detail_html = None

                        try:
                            replace_list = []
                            pro_images_front = []
                            pro_images_back = []

                            # 产品图
                            for img in item.find_all('img'):
                                img_url = img.get('src')
                                new_img_url = 'http://www.guanyipipe.com/' + img_url
                                if not new_img_url: continue
                                if new_img_url and new_img_url not in pro_images_front:
                                    replace_list.append(img_url)
                                    pro_images_front.append(new_img_url)

                            # 下载
                            if pro_images_front:
                                command_thread(company_info['机构简称'], list(set(pro_images_front)))

                            # 替换产品图片
                            if pro_detail_html and replace_list:
                                for img_url in replace_list:
                                    if 'zuiyouliao' in img_url: continue
                                    encode_img_url = 'http://www.guanyipipe.com/' + img_url
                                    if not encode_img_url: continue

                                    hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                                    new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                                    pro_images_back.append(new_img_url)
                                    pro_detail_html = str(pro_detail_html).replace(img_url, new_img_url)

                        except:
                            pro_images_front = None
                            pro_images_back = None
                        finally:
                            pro_detail_html = pro_detail_html.replace('\n', "").replace('\t', "").replace('\r',
                                                                                                          "").replace(
                                '\"', "'")

                        _data = {
                            'pro_link': pro_link,
                            'domain': domain,
                            '机构全称': company_info['机构全称'],
                            '机构简称': company_info['机构简称'],
                            '企业类型': company_info['企业类型'],
                            '企业动态': company_info.get('企业动态'),
                            '产品链接': company_info['产品链接'],
                            '产品名称': pro_name,
                            '产品特点': pro_td,
                            '产品详情': pro_detail_html,
                            '应用行业': pro_yy,
                            'pro_images_front': pro_images_front,
                            'pro_images_back': pro_images_back,
                            'status': 1
                        }
                        # print(_data)
                        MongoPipeline('products').update_item({'pro_link': None}, _data)
                        shutil.rmtree(f"D:/Projects/dev/zyl_34/download_data/{company_info['机构简称']}", True)
                    except Exception as error:
                        log_err(error)
            except Exception as error:
                log_err(error)
        if domain == "www.minqiao.com.cn":
            try:
                for item in soup.find('div', {'class': 'clearfix list-box'}).find_all('a'):
                    pro_name = item.get('title').strip()
                    pro_link = item.get('href')
                    if str(pro_link).startswith('pro'):
                        pro_link = 'http://www.minqiao.com.cn/' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('_108_')[1].split('.')[0])
                if int(current_page) < 4:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('_108_')[0] + f'_108_{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.ruihua650.com":
            try:
                for item in soup.find('ul', {'class': 'photo_display_area jz_scroll'}).find_all('a', {'class': 'list_photo_wrapper'}):
                    pro_name = item.find('span').get_text().strip()
                    pro_link = item.find('div', {'class': 'photo_item'}).get('src-original')

                    if str(pro_link).startswith('//'):
                        pro_link = 'http:' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name,
                        '产品特点': '',
                        '产品详情': '',
                        '应用行业': '',
                        'pro_images_front': [],
                        'pro_images_back': [],
                        'status': 1
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)

            try:
                current_page = int(company_info['产品链接'].split('_108_')[1].split('.')[0])
                if int(current_page) < 4:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('_108_')[0] + f'_108_{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.innovapack.com.cn":
            try:
                for item in soup.find_all('li', {'class': 'w-list-item f-clearfix'}):
                    pro_name = item.find('h5').get_text().strip()
                    pro_link = item.find('a').get('href')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.innovapack.com.cn' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('/p/')[1].split('.')[0])
                if int(current_page) < 7:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.st-gh.com":
            try:
                for item in soup.find('div', {'class': 'e_box e_box-000 p_products'}).find_all('div', {'class': 'e_box e_ProductBox-001 p_Product'}):
                    pro_name = item.find('div', {'class': 'font'}).get_text().strip()
                    pro_link = item.find('h3', {'class': 'e_title e_ImgTitle-001 d_title p_title_1 js-protitle'}).get('data-url')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.st-gh.com' + pro_link
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('/p/')[1].split('.')[0])
                if int(current_page) < 7:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.fjxl.com":
            try:
                for item in soup.find('ul', {'class': 'xypg-product-list clearfix'}).find_all('li'):
                    pro_name = item.find_all('a')[0].get('title').strip()
                    pro_link = item.find_all('a')[0].get('href')
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('/gcgjb94/p')[1].split('.')[0])
                if int(current_page) < 8:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('/gcgjb94/p')[0] + f'/gcgjb94/p{current_page+1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.fzlvfan.com":
            try:
                for item in soup.find('div', {'class': 'ysfllist_list'}).find_all('li'):
                    pro_name = item.find_all('a')[-1].get_text().strip()
                    pro_link = 'http://www.fzlvfan.com/' + item.find_all('a')[-1].get('href')

                    try:
                        replace_list = []
                        pro_images_front = []
                        pro_images_back = []

                        # 产品图
                        img_url = item.find('img').get('src')
                        new_img_url = 'http://www.fzlvfan.com/' + img_url
                        if not new_img_url: continue
                        if new_img_url and new_img_url not in pro_images_front:
                            replace_list.append(img_url)
                            pro_images_front.append(new_img_url)

                            hash_key = hashlib.md5(new_img_url.encode("utf8")).hexdigest()
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)

                        # 下载
                        if pro_images_front:
                            command_thread(company_info['机构简称'], list(set(pro_images_front)))

                    except:
                        pro_images_front = None
                        pro_images_back = None

                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name,
                        'pro_images_front': pro_images_front,
                        'pro_images_back': pro_images_back
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)
        if domain == "www.amesonpak.com":
            try:
                for item in soup.find('ul', {'class': 'pro-ul clear'}).find_all('li'):
                    pro_name = item.find('h3').get_text().strip()
                    pro_link = 'http://www.amesonpak.com/' + item.find('a').get('href')
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('?page=')[1])
                if int(current_page) < 6:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('?page=')[0] + f'?page={current_page+1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.atontech.com.cn":
            try:
                for item in soup.find('div', {'class': 'pro_img'}).find_all('a'):
                    pro_name = item.find('h1').get_text().strip()
                    pro_link = 'http://www.atontech.com.cn' + item.get('href')
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
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
                current_page = int(company_info['产品链接'].split('?page=')[1])
                if int(current_page) < 6:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('?page=')[0] + f'?page={current_page+1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.kaidapack.com":
            try:
                for item in soup.find('ul', {'class': 'product-list clearfix'}).find_all('li'):
                    pro_images_front = []
                    pro_name = item.find('h5').get_text().strip()
                    pro_link = 'http://www.kaidapack.com' + item.find('img').get('src')
                    pro_images_front.append(pro_link)
                    hash_key = hashlib.md5(pro_link.encode("utf8")).hexdigest()
                    new_img_url = serverUrl + hash_key + '.jpg'
                    command_thread(company_info['机构简称'], pro_images_front)
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name,
                        '产品特点': None,
                        '产品详情': None,
                        '应用行业': company_info['pro_yy'],
                        'pro_images_front': [pro_link],
                        'pro_images_back': [new_img_url],
                        'status': 1
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)
    except Exception as error:
        log_err(error)
