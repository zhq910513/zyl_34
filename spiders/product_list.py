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
from urllib.parse import urlparse, urlencode

import requests
from bs4 import BeautifulSoup

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, serverUrl

requests.packages.urllib3.disable_warnings()


# 请求列表
def product_list(company_info):
    try:
        if 'zzxksj.1688.com' in company_info['产品链接']:
            parse_list(company_info, '')
        elif 'lvshengpapercup.1688.com' in company_info['产品链接']:
            parse_list(company_info, '')
        elif 'www.fzghxc.com' in company_info['产品链接']:
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Content-Length': '85',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie': 'JSESSIONID=FDFA1C164837D1F999CE4666EFEF8F1C; sajssdk_2015_cross_ZQSensorsObjnew_user=1; sensorsdata2015jssdkcrossZQSensorsObj=%7B%22distinct_id%22%3A%22180dd3c72393e5-058b45bdd71fd0c-14333270-1382400-180dd3c723ad53%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_landing_page%22%3A%22http%3A%2F%2Fwww.fzghxc.com%2Fproduct%2F7%2F%22%7D%2C%22%24device_id%22%3A%22180dd3c72393e5-058b45bdd71fd0c-14333270-1382400-180dd3c723ad53%22%7D',
                'Host': 'www.fzghxc.com',
                'Origin': 'http://www.fzghxc.com',
                'Referer': 'http://www.fzghxc.com/product/5/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            data = {
                'compId': 'product_list-1542878678071',
                'productCateId': '5',
                'xibcommonId': '5',
                'highlightCategoryId': '5'
            }
            resp = requests.post(company_info['产品链接'], headers=headers, data=urlencode(data), verify=False)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                parse_list(company_info, resp.text)
            else:
                print(resp.status_code)
        elif 'www.dehanguan.com' in company_info['产品链接']:
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Cookie': 'PHPSESSID=cs9t8nn7qesnb9hi5smkm46al6; s_l=zh_CN; s_u=0; wp_layer_content_layer9FDE695CAD19340370D92C773B05EAEC=%7B%22product_category_more%22%3A%225%2C7%2C8%2C6%2C9%2C10%2C11%2C16%2C12%2C13%2C14%22%7D; route=d8d964079d83d5929b7057b3c76d5bbd; wp_layer_page_layer9FDE695CAD19340370D92C773B05EAEC=2',
                'Host': 'www.dehanguan.com',
                'Referer': 'http://www.dehanguan.com/page53',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            resp = requests.get(company_info['产品链接'], headers=headers, verify=False)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                parse_list(company_info, resp.text)
            else:
                print(resp.status_code)
        else:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
            }
            resp = requests.get(company_info['产品链接'], headers=headers, verify=False)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                print(resp.url)
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
            jsonData = json.load(open(f'D:\Projects\dev\zyl_34\spiders\data.json', 'r', encoding="utf-8"))
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
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page + 1}'
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
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page + 1}'
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
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page + 1}'
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
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page + 1}.html'
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
                                    for n_p in item.find_all('p')[num + 1:]:
                                        pro_td.append(n_p.get_text().replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                 '').strip())
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
                                pro_detail_html = pro_detail_html + str(item.find_all('p')[0]) + str(
                                    item.find_all('p')[1])
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
                    company_info['产品链接'] = link.split('_108_')[0] + f'_108_{current_page + 1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.ruihua650.com":
            try:
                for item in soup.find('ul', {'class': 'photo_display_area jz_scroll'}).find_all('a', {
                    'class': 'list_photo_wrapper'}):
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
                    company_info['产品链接'] = link.split('_108_')[0] + f'_108_{current_page + 1}.html'
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
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page + 1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.st-gh.com":
            try:
                for item in soup.find('div', {'class': 'e_box e_box-000 p_products'}).find_all('div', {
                    'class': 'e_box e_ProductBox-001 p_Product'}):
                    pro_name = item.find('div', {'class': 'font'}).get_text().strip()
                    pro_link = item.find('h3', {'class': 'e_title e_ImgTitle-001 d_title p_title_1 js-protitle'}).get(
                        'data-url')
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
                    company_info['产品链接'] = link.split('/p/')[0] + f'/p/{current_page + 1}.html'
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
                    company_info['产品链接'] = link.split('/gcgjb94/p')[0] + f'/gcgjb94/p{current_page + 1}.html'
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
                    company_info['产品链接'] = link.split('?page=')[0] + f'?page={current_page + 1}'
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
                    company_info['产品链接'] = link.split('?page=')[0] + f'?page={current_page + 1}'
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
        if domain == "www.fjzhongya.com":
            try:
                for item in soup.find('div', {'class': 'p_p_list'}).find_all('a'):
                    pro_name = item.get('title').strip()
                    pro_link = item.get('href')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.fjzhongya.com' + pro_link
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
                current_page = int(company_info['产品链接'].split('?page=')[1].split('.')[0])
                if int(current_page) < 14:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('?page=')[0] + f'?page={current_page + 1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.fzghxc.com":
            try:
                for num, item in enumerate(soup.find_all('div', {'class': 'e_box p_Product product'})):
                    pro_name = item.find('div', {'class': 'name'}).get_text().strip()
                    pro_link = item.find('a').get('href')
                    if str(pro_link).startswith('/'):
                        pro_link = 'http://www.fzghxc.com' + pro_link
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
                current_page = int(company_info['产品链接'].split('&currentPage=')[1])
                if int(current_page) < 5:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('&currentPage=')[0] + f'&currentPage={current_page + 1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "xm-devon.com":
            try:
                for item in soup.find_all('div', {'fatherid': 'layerDB58C9E78DF3936C3B7EDBC121B9BD27'}):
                    pro_images_front = []
                    pro_images_back = []
                    pro_name = item.find('div', {'class': 'wp-title_content'}).get_text().strip()
                    pro_link = item.find('a', {'class': 'btnarea button_btndefault-link'}).get('href')
                    img_url = item.find('img').get('src')
                    pro_images_front.append(img_url)

                    hash_key = hashlib.md5(img_url.encode("utf8")).hexdigest()
                    new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                    pro_images_back.append(new_img_url)

                    if pro_link == 'javascript:;':
                        pro_link = img_url

                    pro_yy = item.find_all('div', {'class': 'wp-title_content'})[0].get_text()

                    pro_td = item.find_all('div', {'class': 'wp-title_content'})[2].get_text()

                    pro_detail_html = str(item.find_all('div', {'class': 'wp-title_content'})[1])

                    # 下载
                    if pro_images_front:
                        command_thread(company_info['机构简称'], list(set(pro_images_front)))

                    pro_data = {
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
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)
        if domain == "www.zpwpw.cn":
            try:
                for item in soup.find_all('div', {'class': 'm-theme1-list'}):
                    pro_images_front = []
                    pro_images_back = []
                    pro_name = item.find_all('a')[-1].get_text().strip()
                    pro_link = 'http://www.zpwpw.cn' + item.find_all('a')[-1].get('href')

                    # 产品图
                    for img in item.find_all('img'):
                        img_url = img.get('data-original')
                        if not img_url: continue
                        if img_url and img_url not in pro_images_front:
                            pro_images_front.append(img_url)

                            hash_key = hashlib.md5(img_url.encode("utf8")).hexdigest()
                            new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                            pro_images_back.append(new_img_url)

                    # 下载
                    if pro_images_front:
                        command_thread(company_info['机构简称'], list(set(pro_images_front)))

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
                        'pro_images_front': pro_images_front,
                        'pro_images_back': pro_images_back,
                        'status': 1
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)

            try:
                current_page = int(company_info['产品链接'].split('page=')[1])
                if int(current_page) < 1:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page + 1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.jinguan-cn.com":
            try:
                for item in soup.find_all('div', {'class': 'w-prd-list-cell'}):
                    pro_name = item.find('div', {'class': 'w-prd-imgbox'}).get('title').strip()
                    pro_link = 'http://www.jinguan-cn.com' + item.find_all('a')[0].get('href')
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
                current_page = int(company_info['产品链接'].split('--')[1].split('.')[0])
                if int(current_page) < 16:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('--')[0] + f'--{current_page + 1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.gdyuanchengsy.com":
            try:
                for info in soup.find_all('ul', {'class': 'cplbzs_ul'}):
                    for item in info.find_all('li'):
                        pro_name = item.find('span').get_text().strip()
                        pro_link = 'http://www.gdyuanchengsy.com/' + item.find('a').get('href')
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
        if domain == "www.leyouguandao.com":
            try:
                for item in soup.find('div', {'class': 'ny_pro_list'}).find_all('li'):
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
        if domain == "www.pvc123.com":
            try:
                for info in soup.find_all('div', {'class': 'main_body'}):
                    for item in info.find_all('td'):
                        pro_name = item.find_all('a')[-1].get_text().strip()
                        pro_link = item.find_all('a')[-1].get('href')
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
        if domain == "www.fjhoutiankeji.com":
            try:
                for item in soup.find('div', {'class': 'main pro_cp'}).find_all('li'):
                    pro_name = item.find('p').get_text().strip()
                    pro_link = 'http://www.fjhoutiankeji.com' + item.find_all('a')[-1].get('href')
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
        if domain == "www.dehanguan.com":
            try:
                for item in soup.find_all('div', {'class': 'wp-new-article-style-c'}):
                    pro_name = item.find('a', {'class': 'productlistid memberoff'}).get_text().strip()
                    pro_link = item.find('a', {'class': 'productlistid memberoff'}).get('href')
                    pro_yy = item.find('p', {'class': 'category_p'}).get_text().strip()
                    pro_data = {
                        'pro_link': pro_link,
                        'domain': domain,
                        '机构全称': company_info['机构全称'],
                        '机构简称': company_info['机构简称'],
                        '企业类型': company_info['企业类型'],
                        '企业动态': company_info.get('企业动态'),
                        '产品链接': company_info['产品链接'],
                        '产品名称': pro_name,
                        '应用行业': pro_yy
                    }
                    # print(pro_data)
                    MongoPipeline('products').update_item({'pro_link': None}, pro_data)
            except Exception as error:
                log_err(error)

            try:
                current_page = int(company_info['产品链接'].split('page=')[1])
                if int(current_page) < 12:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('page=')[0] + f'page={current_page + 1}'
                    return product_list(company_info)
            except:
                pass
        if domain == "qzhhwfb.com":
            try:
                for item in soup.find_all('div', {'class': 'w-prd-list-cell'}):
                    pro_name = item.find('div', {'class': 'w-prd-imgbox'}).get('title').strip()
                    pro_link = 'http://qzhhwfb.com' + item.find('a').get('href')
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
        if domain == "msxbz.cn":
            try:
                for item in soup.find_all('div', {'class': 'w-prd-list-cell'}):
                    pro_name = item.find('div', {'class': 'w-prd-imgbox'}).get('title').strip()
                    pro_link = 'http://msxbz.cn' + item.find('a').get('href')
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
        if domain == "www.qzjtsj.cn":
            try:
                for item in soup.find('div', {'id': 'model_contant_main'}).find_all('li'):
                    pro_name = item.find('strong').get_text().strip()
                    pro_link = 'http://www.qzjtsj.cn' + item.find('a').get('href')
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
                current_page = int(company_info['产品链接'].split('_')[1].split('.')[0])
                if int(current_page) < 5:
                    link = company_info['产品链接']
                    company_info['产品链接'] = link.split('_')[0] + f'_{current_page + 1}.html'
                    return product_list(company_info)
            except:
                pass
        if domain == "www.fjlbgy.com":
            try:
                for item in soup.find_all('div', {'class': 'product-thumb product-wrapper'}):
                    pro_name = item.find_all('a')[-1].get_text().strip()
                    pro_link = 'http://www.fjlbgy.com' + item.find_all('a')[-1].get('href')
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
        if domain == "www.chinatkp.com":
            try:
                for item in soup.find_all('div', {'class': 'view'}):
                    pro_name = item.find_all('a')[-1].get_text().strip()
                    pro_link = 'http://www.chinatkp.com/piclist.asp' + item.find_all('a')[-1].get('href')
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
        if domain == "www.jjxingtai.com":
            try:
                for item in soup.find('div', {'class': 'am-u-sm-12 am-u-md-12 am-u-lg-9'}).find_all('li'):
                    pro_name = item.find('p').get_text().strip()
                    pro_link = 'http://www.jjxingtai.com' + item.find('a').get('href').replace('..', '')
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
        if domain == "lvshengpapercup.1688.com":
            jsonData = json.load(open(r'D:\Projects\zyl_34\spiders\data.json', 'r', encoding="utf-8"))
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
    except Exception as error:
        log_err(error)
