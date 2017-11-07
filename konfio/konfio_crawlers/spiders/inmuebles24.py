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
    MAX_ADS = MAX_PAGE * 20  # Numero maximo de anuncios que soporta la paginacion de este sitio

    def start_requests(self):  # Inicio del spider
        for url in self.start_urls:  # Iteracion sobre las url's de iniciales
            yield Request(url, self.parse)  # Request al metodo parse

    def parse_ad(self, response):
        item = GeneralItem()  # Se declara el item que se utilizara
        item["id_item"] = response.meta.get('deltafetch_key')  # Se obtiene el id desde los metadatos del request
        item['price'] = response.xpath(
            '//p[@class="precios no-margin"]//span[@class="valor"]/text()').extract_first()  # Se obtiene el precio

        item["title"] = response.xpath('//div[@class="card-title"]/h1/text()').extract_first().replace("'",
                                                                                                       "")  # Se obtiene el titulo

        description = response.xpath(
            'string(//div[@class="card description"]//span)').extract_first()  # Se obtiene la descripcion
        if description:
            item['description'] = description.strip().replace("'",
                                                              "")  # Se limpian los espacios en blanco al inicio y al final de la descripcion y se quita la comilla simple para evitar problemas con la base de datos
        else:
            item['description'] = None
        item['site'] = 'inmuebles24'  # Se declara el sitio
        item['url'] = response.url  # Se obtiene la url del anuncio
        yield item  # Se regresa el item con todos los campos

    @staticmethod
    def generate_page(n, subcategory):
        """
        Se da formato a la url de acuerdo al numero de pagina
        :param n: Numero de pagina
        :param subcategory: Url actual
        :return: Se regresa la url con el formato correcto
        """
        if n != 1:
            url = re.sub(r'.html', '-pagina-{0}.html', subcategory, re.IGNORECASE)
            if url:
                return url.format(n)
        else:
            return subcategory

    @staticmethod
    def order_by_fecha(url):
        """
        Este metodo le da formato a la url para ordenar por fecha la aparicion de los anuncios
        :param url: Url de la pagina
        :return: Regresa la url formateada
        """
        if url:
            url = re.sub(r'.html', '-ordenado-por-fechaonline-descendente.html', url, re.IGNORECASE)
        else:
            url = None
        return url

    @staticmethod
    def get_n_pagination(total, per_page):
        """
        Regresa el numero total de paginas tomando en cuenta el numero de anuncios y el numero de anuncios por pagina
        :param total:  Numero total de anuncios
        :param per_page: Numero de anuncios por pagina
        :return: Regresa el numero total de anuncios como entero
        """
        return int(math.ceil(total / per_page))

    @staticmethod
    def get_n(response):
        """
        Obtiene el numero total de anuncios
        :param response: Response de la pagina
        :return: Regresa el numero de anuncios
        """
        n_props = response.xpath('//h1[@class="resultado-title"]/strong/text()').extract_first()
        if n_props:
            n_props = re.sub('\D+', '', n_props)
            return int(n_props) if n_props else 0
        return 0

    def parse_next(self, response):
        urls = response.xpath('//ul[@class="list-posts"]//h4/a/@href').extract()  # Se obtienen las urls
        urls = ["http://www.inmuebles24.com" + url_i for url_i in urls]  # Se les da formato a las urls
        ids = [re.search(r'-(\d+)\.html$', x).group(1) if re.search(r'-(\d+)\.html$', x) else None for x in
               urls]  # Se obtienen los ids usando regex
        for url_i, id_i in zip(urls, ids):  # Se itera sobre las urls y los ids
            yield Request(url_i, self.parse_ad, meta={
                'deltafetch_key': id_i})  # Se hace request a parse_ad enviando el id como metadato y almacendandolo en el deltafetch

    def parse(self, response):
        estados = response.xpath(
            '(//div[@class="facetas-search"]//ul[@class="facetas-ul"])[1]//@href').extract()  # Se obtienen los estados
        for estado in estados:  # Se itera sobre los estados
            yield Request(self.order_by_fecha("http://www.inmuebles24.com" + estado),
                          self.parse2)  # Se hace un request al metodo parse 2

    def parse2(self, response):
        n_properties = self.get_n(response)  # Se obtiene el numero total de propiedades
        if n_properties > 0:
            if n_properties > self.MAX_ADS:
                ciudades = response.xpath(
                    '(//div[@class="facetas-search"]//ul[@class="facetas-ul"])[1]//@href').extract()  # Se obtienen las ciudades
                for ciudad in ciudades:  # Se itera sobre las ciudades
                    yield Request(self.order_by_fecha("http://www.inmuebles24.com" + ciudad),
                                  self.parse3)  # Se hace un request a parse3
            else:
                for i in range(1,
                               self.get_n_pagination(self.get_n(response), 20)):  # Se itera sobre el numero de paginas
                    yield Request(self.generate_page(i, response.url),
                                  callback=self.parse_next)  # Se hace un request a parse_next

    def parse3(self, response):
        for i in range(1, self.get_n_pagination(self.get_n(response),
                                                20)):  # Se genera les da formato a las urls y se itera sobre ellas
            yield Request(self.generate_page(i, response.url),
                          callback=self.parse_next)  # Se hace un request a parse_next
