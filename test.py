from spiders.download import command_thread

pro_images_front = [   'http://www.fjzhongya.com/upload/products/2015073109534714.jpg']

if pro_images_front:
    command_thread('中亚', list(set(pro_images_front)))

