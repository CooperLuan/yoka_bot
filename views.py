import re

from pymongo import MongoClient
import pandas as pd

db = MongoClient('mongodb://127.0.0.1/yoka_bot').yoka_bot

rows = list(db.webpages.find({
    'item_name': 'YokaBotBrandListItem',
}))
df_brand_list = pd.DataFrame(rows)

rows = list(db.webpages.find({
    'item_name': 'YokaBotBrandItem',
}))
df_brand = pd.DataFrame(rows)
df_brand['alias'] = df_brand['url'].apply(lambda x: x.partition('com/')[-1].strip('/ '))

rows = list(db.webpages.find({
    'item_name': 'YokaBotProductListItem',
}))
df_product_list = pd.DataFrame(rows)
df_product_list['alias'] = df_product_list['url'].apply(lambda x: re.search(r'\.com/(.+?)/', x).group(1))
df_product_list['product_id'] = df_product_list['product_url'].apply(lambda x: re.search(r'detail(\d+)', x).group(1))

rows = list(db.webpages.find({
    'item_name': 'YokaBotProductItem',
}))
df_products = pd.DataFrame(rows)
df_products['categories'] = df_products['breadcrumb'].apply(lambda x: x and '-'.join(x).partition(u'首页-')[-1] or x)
df_products['attrib2'] = df_products['attrib'].apply(
    lambda x: [(
        isinstance(t[0], list) and ''.join(t[0]).strip(u'\uff1a') or t[0],
        isinstance(t[1], list) and ''.join(t[1]).strip(u'\uff1a') or t[1],
    ) for t in x
    if isinstance(t, list) and len(t) == 2]
)

df = df_brand.merge(
    df_product_list, how='inner',
    on='alias',
)[['brand_cn', 'brand_en', 'title', 'product_id']].merge(
    df_products, how='inner',
    on='product_id', suffixes=('', '_2'),
)[['brand_cn', 'brand_en', 'categories', 'title', 'product_id']]
