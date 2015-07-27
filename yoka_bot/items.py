# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YokaBotItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class YokaBotBrandListItem(scrapy.Item):
    item_name = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    is_hot = scrapy.Field()
    pass


class YokaBotBrandItem(scrapy.Item):
    item_name = scrapy.Field()
    url = scrapy.Field()
    avator = scrapy.Field()
    brand_cn = scrapy.Field()
    brand_en = scrapy.Field()
    country = scrapy.Field()
    created = scrapy.Field()
    official_url = scrapy.Field()
    story = scrapy.Field()
    product_list_url = scrapy.Field()
    pass


class YokaBotProductListItem(scrapy.Item):
    item_name = scrapy.Field()
    url = scrapy.Field()
    page = scrapy.Field()
    product_url = scrapy.Field()
    img = scrapy.Field()
    title = scrapy.Field()
    pass


class YokaBotProductItem(scrapy.Item):
    item_name = scrapy.Field()
    url = scrapy.Field()
    product_id = scrapy.Field()
    breadcrumb = scrapy.Field()
    title = scrapy.Field()
    attrib = scrapy.Field()
    img = scrapy.Field()
