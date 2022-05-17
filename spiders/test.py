from dbs.pipelines import MongoPipeline

for pro_info in MongoPipeline('products').find({}):
    MongoPipeline('products').unset_item({'_id': pro_info['_id']}, {'pro_name': '', 'pro_td': '', 'pro_detail_html': ''})
