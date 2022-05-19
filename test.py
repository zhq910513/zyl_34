import hashlib
import pprint
import shutil

from dbs.pipelines import MongoPipeline
from spiders.download import command_thread, serverUrl
pp=pprint.PrettyPrinter(indent=4)

while True:
    for pro_info in MongoPipeline('case_detail').find({'pro_images_back': None}).limit(10):
        try:
            pro_images_front = []
            pro_images_back = []
            litpic = pro_info.get("litpic")
            if litpic:
                litpic = 'https://www.soliao.com' + litpic
                pro_images_front.append(litpic)

            b = pro_info.get("b")
            if b:
                g = b.get("g")
                if g:
                    fileName = g.get("fileName")
                    fileName = 'https://slfiles.soliao.com/soliao/case/other/' + fileName
                    pro_images_front.append(fileName)

            b = pro_info.get("b")
            if b:
                i = b.get("i")
                if i:
                    i = i[0]
                    pro_images_front.append(i)

            for img_url in pro_images_front:
                hash_key = hashlib.md5(img_url.encode("utf8")).hexdigest()
                new_img_url = serverUrl + hash_key + '.' + img_url.split('.')[-1]
                pro_images_back.append(new_img_url)

            # 下载
            if pro_images_front:
                command_thread('souliao', list(set(pro_images_front)))

            xcyy = pro_info.get('选材原因')
            xcyy_list = []
            if xcyy:
                if '2-' in xcyy:
                    s = xcyy.split('2-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                    xcyy_list.append(s)
                    xcyy = '2-' + xcyy.split('2-')[1]
                    if '3-' in xcyy:
                        s = xcyy.split('3-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                        xcyy_list.append(s)
                        xcyy = '3-' + xcyy.split('3-')[1]
                        if '4-' in xcyy:
                            s = xcyy.split('4-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                            xcyy_list.append(s)
                            xcyy = '4-' + xcyy.split('4-')[1]
                            if '5-' in xcyy:
                                s = xcyy.split('5-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                                xcyy_list.append(s)
                                xcyy = '5-' + xcyy.split('5-')[1]
                                if '6-' in xcyy:
                                    s = xcyy.split('6-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                                    xcyy_list.append(s)
                                    xcyy = '6-' + xcyy.split('6-')[1]
                                    if '7-' in xcyy:
                                        s = xcyy.split('7-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                                        xcyy_list.append(s)
                                        xcyy = '7-' + xcyy.split('7-')[1]
                                        if '8-' in xcyy:
                                            s = xcyy.split('8-')[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
                                            xcyy_list.append(s)
                                            xcyy = '8-' + xcyy.split('8-')[1]
                                            if '9-' in xcyy:
                                                s = xcyy.split('9-')[0].replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                    '').strip()
                                                xcyy_list.append(s)
                                                xcyy = '9-' + xcyy.split('9-')[1]
                                                if '10-' in xcyy:
                                                    s = xcyy.split('10-')[0].replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                        '').strip()
                                                    xcyy_list.append(s)
                                                    xcyy = '10-' + xcyy.split('10-')[1]
                                                    if '11-' in xcyy:
                                                        s = xcyy.split('11-')[0].replace('\n', '').replace('\t', '').replace('\r',
                                                                                                                            '').strip()
                                                        xcyy_list.append(s)
                                                        xcyy = '11-' + xcyy.split('11-')[1]
                                                        if '12-' in xcyy:
                                                            s = xcyy.split('12-')[0].replace('\n', '').replace('\t', '').replace(
                                                                '\r', '').strip()
                                                            xcyy_list.append(s)
                                                            xcyy = '12-' + xcyy.split('12-')[1]

            pro_info['选材原因'] = xcyy_list
            pro_info['pro_images_front'] = pro_images_front
            pro_info['pro_images_back'] = pro_images_back

            MongoPipeline('case_detail').update_item({'_id': None}, pro_info)
        except Exception as error:
            print(error)
    shutil.rmtree(f"D:/Projects/dev/zyl_34/download_data/souliao", True)