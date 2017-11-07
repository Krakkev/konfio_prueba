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

    def start_requests(self):  # Inicio del spider
        for url in self.start_urls:  # Iteracion sobre las url's de iniciales
            yield Request(url, self.parse)  # Request al metodo parse

    def parse_anuncio(self, response):
        item = GeneralItem()  # Se declara el item

        item["id_item"] = response.meta['deltafetch_key']  # Se obtiene el id de los metas
        description = response.xpath(
            '//pre[@itemprop="description"]/text()').extract_first()  # Se obtiene la descripcion
        if description:
            item["description"] = description.strip().replace("'",
                                                              "")  # Se quita la comilla simple para evitar problemas con la base de datos
        else:
            item["description"] = None

        item['price'] = response.xpath('//meta[@name="precio"]/@content').extract_first()  # Se obtiene el precio

        item["title"] = (response.xpath('(//div[@class="col-sm-12"]//h1//text())[1]').extract()[0].capitalize() +
                         response.xpath('(//div[@class="col-sm-12"]//h1//text())[2]').extract()[0]).replace("'",
                                                                                                            "")  # Se obtiene el titulo
        item["site"] = 'century21'  # Se declara el sitio
        item['url'] = response.url  # Se obtiene la url del anuncio
        yield item  # Se regresa el item con todos los campos

    @staticmethod
    def generate_page(n, subcategory):  # Method depends on site
        """
        Se da formato a la url de acuerdo al numero de pagina
        :param n: Numero de pagina
        :param subcategory: Url actual
        :return: Se regresa la url con el formato correcto
        """
        if n != 1:
            url = subcategory + '?pagina={0}'
            if url:
                return url.format(n)
        else:
            return subcategory

    def get_n(self, response):
        """
        Obtiene el numero total de anuncios
        :param response: Response de la pagina
        :return: Regresa el numero de anuncios
        """
        try:
            aux = response.xpath('//span[@class="text-uppercase"]/strong/text()').extract_first()
            n_props_string = re.search(r'(\d*$)', aux).group(1)
            n_props = int(n_props_string)
            return int(math.ceil(n_props / 21.0))  # Number depends on site
        except:
            return 1

    def parse_next(self, response):
        urls = response.xpath('//div[@class="thumbnail"]/a/@href').extract()  # Se obtienen las urls de los anuncios
        urls = ["http://century21mexico.com" + url_i for url_i in urls]  # Se le da formato a las urls
        ids = [re.search(r'/(\d+)_', x).group(1) if re.search(r'/(\d+)_', x) else None for x in
               urls]  # Se obtienen los ids de los anuncios
        for url_i, id_i in zip(urls, ids):  # Se itera sobre las urls y los ids
            yield Request(url_i, self.parse_anuncio, meta={
                'deltafetch_key': id_i})  # Se hace un request a parse_anuncio enviando el id a traves de los metas para asi almacenarlo en el deltafetch

    def parse(self, response):
        for i in range(1, self.get_n(response) + 1):  # Se intera sobre el numero de paginas
            yield Request(self.generate_page(i, response.url),
                          callback=self.parse_next)  # Se genera la url de la pagina y se hace un request a parse_next
