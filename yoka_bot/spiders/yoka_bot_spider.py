# encoding: utf8
import re
import pandas as pd
from lxml import etree
import scrapy
from yoka_bot.items import YokaBotBrandListItem, YokaBotBrandItem, YokaBotProductListItem, YokaBotProductItem

host = 'http://brand.yoka.com'

def wrap_full_url(url):
    if url.startswith('http'):
        return url
    return host + url


class YokaBotSpider(scrapy.Spider):
    name = "YokaBot"
    start_urls = [
        "http://brand.yoka.com/brandlist.htm",
    ]

    def parse(self, response):
        html = response.body_as_unicode()
        tree = etree.HTML(html)
        nodes = tree.xpath("//a[@target='_blank']")
        nodes = [
            (node.text.strip('\n\r\t '), node.attrib['href'])
            for node in nodes
            if node.text and node.text.strip('\n\r\t ')
        ]
        df = pd.DataFrame(nodes, columns=['name', 'link'])
        valid_links = df[df['link'].apply(lambda x: x != '/' and x.count('/') == 1)]['link'].unique()
        for link in valid_links:
            is_hot = False
            name = df[df['link'] == link]['name'].apply(
                lambda x: re.sub(r'[\n\r\t]+', r'', x.strip('\n\r\t '), re.S)).tolist()
            name = map(lambda x: re.sub(r'\s{2,}', r' ', x, re.S), name)
            if df[df['link'] == link]['name'].unique().size > 1:
                is_hot = True
            item = YokaBotBrandListItem(**{
                'item_name': 'YokaBotBrandListItem',
                'name': name,
                'link': wrap_full_url(link),
                'is_hot': is_hot,
            })
            yield item
            yield scrapy.Request(item['link'], callback=self.parse_brand_page)

    def parse_brand_page(self, response):
        url = response.url
        tree = etree.HTML(response.body_as_unicode())
        avator = tree.xpath("//div[@class='m-product-show']/div//img/@src")
        attrs = [node.text for node in tree.xpath("//div[@class='m-product-show']/div[@class='pl']/div[@class='box']/dl//dd//li")]
        attrs = dict([attr.partition(u'\uff1a')[::2] for attr in attrs])
        brand_cn = attrs.get(u'中文名')
        brand_en = attrs.get(u'英文名')
        country = attrs.get(u'国家')
        created = attrs.get(u'创建年代')
        official_url = tree.xpath("//div[@class='m-product-show']//h2/a/@href")
        story = '\n'.join(tree.xpath("//div[@class='m-product-show']//h3/following-sibling::p/text()"))
        product_list_url = tree.xpath("//div[@id='tabcn']//div[@class='more']/a/@href")
        product_list_url = wrap_full_url(url.rstrip('/') + '/productlist.htm?p=1')
        yield YokaBotBrandItem(**{
            'item_name': 'YokaBotBrandItem',
            'url': url,
            'avator': avator and avator[0] or None,
            'brand_cn': brand_cn,
            'brand_en': brand_en,
            'country': country,
            'created': created,
            'official_url': official_url and official_url[0] or None,
            'story': story,
            'product_list_url': product_list_url,
        })
        yield scrapy.Request(product_list_url, callback=self.parse_product_list_page)

    def parse_product_list_page(self, response):
        url = response.url
        page = int(re.search(r'p=(\d+)', url).group(1))

        tree = etree.HTML(response.body_as_unicode())
        nodes = tree.xpath("//div[@class='mask']/dl")
        # force_break = False
        for node in nodes:
            product_url = wrap_full_url(node.xpath(".//dt/a/@href")[0])
            yield YokaBotProductListItem(**{
                'item_name': 'YokaBotProductListItem',
                'url': url,
                'page': page,
                'product_url': product_url,
                'img': node.xpath(".//dt/a/img/@src")[0],
                'title': node.xpath(".//dt/a/img/@alt")[0],
            })
            yield scrapy.Request(product_url, callback=self.parse_product_page)
        if nodes:
            page += 1
            url = re.sub(r'p=(\d+)', r'p=%s' % page, url, re.S)
            yield scrapy.Request(url, callback=self.parse_product_list_page)

    def parse_product_page(self, response):
        url = response.url
        tree = etree.HTML(response.body_as_unicode())
        if tree.xpath("//input[@id='proid']/@value"):
            pid = tree.xpath("//input[@id='proid']/@value")
            breadcrumb = [t.text.strip('\n\r\t ') for t in tree.xpath("//div[@class='zpyTitle']/a")]
            title = [t.strip('\n\r\t ') for t in tree.xpath("//span[@itemprop='name']/text()")]
            attrib = [(t.xpath(".//dt/text()"), [t.strip('\n\r\t ') for t in t.xpath(".//dd")[0].itertext() if t.strip('\n\r\t ')]) for t in tree.xpath("//div[@class='list']/dl")]
            img = tree.xpath("//dt[@id='products_big']//img/@src")
            yield YokaBotProductItem(**{
                'item_name': 'YokaBotProductItem',
                'url': url,
                'product_id': pid and pid[0] or None,
                'breadcrumb': breadcrumb,
                'title': title and title[0].strip('\n\r\t ') or None,
                'attrib': attrib,
                'img': img and img[0] or None,
            })
        else:
            pid = tree.xpath("//input[@id='_productId']/@value")
            title = tree.xpath("//div[@class='gc-brand-profile']/h1/text()")
            breadcrumb = list(filter(lambda x: 'no ' not in x[0], [(node.xpath(".//./@class")[0], node.xpath(".//./text()")[0]) for node in tree.xpath("//div[@class='sub-nav']/div[@class='list']/a")]))
            breadcrumb = breadcrumb and [breadcrumb[0][1]] or None
            attrib = [tuple(node.itertext()) for node in tree.xpath("//div[@class='mask']/ul/li")]
            img = tree.xpath("//dl[@id='gl-brand-showbig']//img/@src")
            yield YokaBotProductItem(**{
                'item_name': 'YokaBotProductItem',
                'url': url,
                'product_id': pid and pid[0] or None,
                'breadcrumb': breadcrumb,
                'title': title and title[0].strip('\n\r\t ') or None,
                'attrib': attrib,
                'img': img and img[0] or None,
            })
