# -*- coding: utf-8 -*-
from konfio_crawlers.items import GeneralItem
from scrapy import Spider, Request
import re
import math
import json

__author__ = 'kgarcia'


class Century21Spider(Spider):
    name = "century21"  # Name depends on site
    allowed_domains = []  # Url depends on site
    start_urls = [
        "http://www.century21mexico.com/venta",
        "http://www.century21mexico.com/renta"
    ]


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse)



    def parse_anuncio(self, response):
        item = GeneralItem()

        item["id_item"] = response.meta['deltafetch_key']
        description = response.xpath('//pre[@itemprop="description"]/text()').extract_first()
        if description:
            item["description"] = description.strip().replace("'","")
        else:
            item["description"] = None
        price = response.xpath('//meta[@name="precio"]/@content').extract_first()
        if price and isinstance(price, basestring):
            re_min_price = re.search('^\D*([\d\.,]*)', price)
            if re_min_price:
                try:
                    item['price'] = int(re_min_price.group(1).replace(',', ''))

                except:
                    item['price'] = 0
        elif price:
            try:
                item['price'] = int(price)
            except:
                item['price'] = 0
        else:
            item['price'] = None
        item["title"] = (response.xpath('(//div[@class="col-sm-12"]//h1//text())[1]').extract()[0].capitalize() +
                         response.xpath('(//div[@class="col-sm-12"]//h1//text())[2]').extract()[0]).replace("'","")
        item["site"] = 'century21'
        yield item

    @staticmethod
    def generate_page(n, subcategory):  # Method depends on site
        if n != 1:
            url = subcategory+'?pagina={0}'
            if url:
                return url.format(n)
        else:
            return subcategory


    def get_n(self, response):
        try:
            aux = response.xpath('//span[@class="text-uppercase"]/strong/text()').extract_first()
            n_props_string = re.search(r'(\d*$)', aux).group(1)
            n_props = int(n_props_string)
            return int(math.ceil(n_props/21.0))  # Number depends on site
        except:
            return 1

    def parse_next(self, response):
        urls = response.xpath('//div[@class="thumbnail"]/a/@href').extract()
        urls = ["http://century21mexico.com" + url_i for url_i in urls]  # Url depends on site
        ids = [re.search(r'/(\d+)_', x).group(1) if re.search(r'/(\d+)_', x) else None for x in urls]  # Regex depends on site
        for url_i, id_i in zip(urls, ids):
            yield Request(url_i, self.parse_anuncio, meta={'deltafetch_key': id_i})

    def parse(self, response):
        for i in range(1, self.get_n(response) + 1):
            yield Request(self.generate_page(i, response.url), callback=self.parse_next)