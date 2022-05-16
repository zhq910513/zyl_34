import hashlib
import re
serverUrl = 'https://zuiyouliao-prod.oss-cn-beijing.aliyuncs.com/zx/image/'
from dbs.pipelines import MongoPipeline

# 格式化图片链接
def format_img_url(product_info, img_url):
    try:
        scheme = product_info['pro_link'].split('//')[0]
        if 'http' not in img_url and 'https' not in img_url:
            if str(img_url).startswith(':'):
                img_url = scheme + img_url[1:]
            # //www.njkwls.com/ueditor/net/upload/image/20211029/6377112184815958829319505.jpg
            elif str(img_url).startswith('//'):
                img_url = scheme + img_url
            elif str(img_url).startswith('/'):
                # /ueditor/net/upload/image/20211029/6377112184815958829319505.jpg
                if product_info['domain'] not in img_url:
                    img_url = scheme + f"//{product_info['domain']}" + f"{img_url}"
                # /www.njkwls.com/ueditor/net/upload/image/20211029/6377112184815958829319505.jpg
                else:
                    img_url = f"{scheme}/" + img_url
            else:
                # ueditor/net/upload/image/20211029/6377112184815958829319505.jpg
                if product_info['domain'] not in img_url:
                    img_url = scheme + f"//{product_info['domain']}" + f"/{img_url}"
                # www.njkwls.com/ueditor/net/upload/image/20211029/6377112184815958829319505.jpg
                else:
                    img_url = f"{scheme}//" + img_url
        return img_url
    except:
        return None


for i in MongoPipeline('products').find({'domain': 'www.jwell.cn'}):
    try:
        print('*****'*40)
        print(i['pro_name'])
        pro_images_back = []

        # 替换非产品图片
        if not i.get('pro_jscs_html'):continue
        pro_jscs_html = i.get('pro_jscs_html')
        images_back = i.get('pro_images_back')
        new_replace_list = re.findall('src=\"(.*?)\"', pro_jscs_html, re.S)
        if new_replace_list:
            for img_url in new_replace_list:
                if 'zuiyouliao' in img_url: continue
                encode_img_url = format_img_url(i, img_url)
                if not encode_img_url: continue
                hash_key = hashlib.md5(encode_img_url.encode("utf8")).hexdigest()
                new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                if hash_key not in images_back:
                    print(f'未存储图片 {img_url, encode_img_url, new_img_url}')
    except Exception as error:
        print(error)
        print(i)