# -*- coding: utf-8 -*-
import re
import math
from konfio_crawlers.items import GeneralItem
from scrapy import Spider, Request
import json
import scrapy
import requests

__author__ = 'kgarcia'


class Inmuebles24Spider(Spider):
    name = "inmuebles24"
    allowed_domains = []
    start_urls = [
        "http://www.inmuebles24.com/inmuebles.html"
    ]


    MAX_PAGE = 1000
    MAX_ADS = MAX_PAGE * 20

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse)

    def parse_anuncio(self, response):
        item = GeneralItem()
        item["id_item"] = response.meta.get('deltafetch_key')
        price = response.xpath('//p[@class="precios no-margin"]//span[@class="valor"]/text()').extract_first()
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
        item["title"] = response.xpath('//div[@class="card-title"]/h1/text()').extract_first().replace("'","")

        descripcion = response.xpath('string(//div[@class="card description"]//span)').extract_first()
        if descripcion:
            item['description'] = descripcion.strip().replace("'","")
        else:
            item['descripcion'] = None
        item['site'] = 'inmuebles24'
        yield item

    @staticmethod
    def generate_page(n, subcategory):
        if n != 1:
            url = re.sub(r'.html', '-pagina-{0}.html', subcategory, re.IGNORECASE)
            if url:
                return url.format(n)
        else:
            return subcategory


    @staticmethod
    def order_by_fecha(url):
        if url:
            url = re.sub(r'.html', '-ordenado-por-fechaonline-descendente.html', url, re.IGNORECASE)
        else:
            url = None
        return url

    @staticmethod
    def get_n_pagination(total, per_page):
        return int(math.ceil(total / per_page))

    @staticmethod
    def get_n(response):
        n_props = response.xpath('//h1[@class="resultado-title"]/strong/text()').extract_first()
        if n_props:
            n_props = re.sub('\D+', '', n_props)
            return int(n_props) if n_props else 0
        return 0

    def parse_next(self, response):
        urls = response.xpath('//ul[@class="list-posts"]//h4/a/@href').extract()
        urls = ["http://www.inmuebles24.com" + url_i for url_i in urls]
        ids = [re.search(r'-(\d+)\.html$', x).group(1) if re.search(r'-(\d+)\.html$', x) else None for x in urls]
        for url_i, id_i in zip(urls, ids):
            yield Request(url_i, self.parse_anuncio, meta={'deltafetch_key': id_i})

    def parse(self, response):
        estados = response.xpath('(//div[@class="facetas-search"]//ul[@class="facetas-ul"])[1]//@href').extract()
        for estado in estados:
            yield Request(self.order_by_fecha("http://www.inmuebles24.com" + estado), self.parse2)

    def parse2(self, response):
        n_properties = self.get_n(response)
        if n_properties > 0:
            if n_properties > self.MAX_ADS:
                ciudades = response.xpath('(//div[@class="facetas-search"]//ul[@class="facetas-ul"])[1]//@href').extract()
                for ciudad in ciudades:
                    yield Request(self.order_by_fecha("http://www.inmuebles24.com" + ciudad), self.parse3)
            else:
                for i in range(1, self.get_n_pagination(self.get_n(response), 20)):
                    yield Request(self.generate_page(i, response.url), callback=self.parse_next)

    def parse3(self, response):
        for i in range(1, self.get_n_pagination(self.get_n(response), 20)):
            yield Request(self.generate_page(i, response.url), callback=self.parse_next)
