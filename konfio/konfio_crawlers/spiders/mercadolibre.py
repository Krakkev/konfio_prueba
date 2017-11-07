import re
from konfio_crawlers.items import GeneralItem
from scrapy import Spider, Request
import json
import math
import requests

__author__ = 'kgarcia'


def clean_text(x):
    """
    Esta funcion sirve para limpiar el texto de espacios en blanco
    :param x: Texto a limpiar
    :return: Regresa el texto limpio de espacios en blanco
    """
    x = re.sub(r'(^\s+)|(\s+$)|(  +)|(\r)|({ +})', '', ''.join(x.strip())) if x else x # Regex para sustituir espacis en blanco
    try:
        return re.sub(r'(\s+,\s+)', ', ', x)
    except:
        return x


class MercadoLibre(Spider):
    name = "mercadolibre"
    allowed_domains = []
    start_urls = [
        "http://inmuebles.mercadolibre.com.mx/venta/",
        "http://inmuebles.mercadolibre.com.mx/renta/"
    ]

    def start_requests(self):#Inicio del spider
        for url in self.start_urls:#Iteracion sobre las url's de iniciales
            yield Request(url, self.parse, dont_filter=True) #Request al metodo parse

    def parse_ad(self, response):
        item = GeneralItem()#Se declara el time
        item["id_item"] = response.meta.get('deltafetch_key')#Se obtiene el id del metadato del deltafetch

        r = requests.get("https://api.mercadolibre.com/items/" + response.meta.get('deltafetch_key').replace("-", ""))#Se hace un request a la API de mercadolibre utilizando el id
        melijson = json.loads(r.text)#Se carga el json a partir del texto del response y se almacena en la variable melijson

        item['title'] = melijson.get("title").replace("'", "") #Se obtiene el titulo del json
        item['price'] = str(melijson.get("price")) #Se obtiene el precio del json y se castea a string

        if response.xpath('//div[@class="vip-description-container"]//text()').extract():
            description = ""
            for desc in response.xpath('//div[@class="vip-description-container"]//text()').extract(): #Se obtiene la descripcion
                if "<img" not in desc:#Se valida que sea una descripcion y no una imagen
                    description = description + "\n" + desc
            description = clean_text(description) #Se limpia la descripcion
        else:
            description = response.xpath('//pre[@class="preformated-text"]/text()').extract_first()#Se obtiene descripcion

        if description:
            item['description'] = description.replace("'", "")#Se remplaza el ' para no tener problemas al insertar a la base de datos
        item['site'] = 'mercadolibre' #Se declara el sitio
        item['url'] = response.url #Se obtiene el url del anuncio
        yield item

    @staticmethod
    def generate_page(ith, url_aux):
        """
        Se da formato a la url de acuerdo al numero de pagina
        :param n: Numero de pagina
        :param subcategory: Url actual
        :return: Se regresa la url con el formato correcto
        """
        return re.sub('_Price', '_Desde_' + str(((ith - 1) * 48) + 1) + '_Price', url_aux)

    @staticmethod
    def get_n(response):
        """
        Obtiene el numero total de anuncios
        :param response: Response de la pagina
        :return: Regresa el numero de anuncios
        """
        try:
            n_str = response.xpath('//div[@class="quantity-results"]/text()').extract_first()
            if n_str:
                n_str = re.search('(.*) resultado', n_str).group(1).replace(',', '')
                return int(math.ceil(int(n_str) / 48.0))
            else:
                return 1
        except:
            return 1

    def parse_next(self, response):
        urls = response.xpath('//a[@class="item-link item__js-link"]/@href').extract() #Se obtienen las urls de los anuncios
        if urls:
            for url in urls: #Se itera sobre los anuncios
                id_i = re.search(r'MLM-\d{9}', url) #Se busca el id con regex
                if id_i:
                    id_i = id_i.group(0) #Se obtiene el grupo del id
                    yield Request(url, self.parse_ad, dont_filter=True, meta={'deltafetch_key': id_i}) #Se hace un request a parse_ad enviando como meta el id, dando pie al almacenamiento del mismo en el deltafetch

    def parse(self, response):
        ranges = ["_PriceRange_0-100000",
                  "_PriceRange_100000-200000",
                  "_PriceRange_200000-300000",
                  "_PriceRange_300000-400000",
                  "_PriceRange_400000-1000000",
                  "_PriceRange_1000000-2000000",
                  "_PriceRange_2000000-3000000",
                  "_PriceRange_3000000-4000000",
                  "_PriceRange_4000000-7000000",
                  "_PriceRange_15000000-0"] # Se declaran los rangos de precios que se usaran para la paginacion
        types = response.xpath('//dl[@id="id_9991459-AMLM_1459_1"]//a/@href').extract() #Se obtienen los tipos
        for type_url in types: #Se itera sobre las url's tipos
            if type_url != '#': #Se verifica que la url sea la correcta
                for range in ranges: #Se itera sobre los rangos de precio
                    yield Request(type_url + range, self.parse2, dont_filter=True) #Se hace un request a parse2

    def parse2(self, response):
        for i in range(1, self.get_n(response) + 1): #Se itera sobre el numero de pagina
            yield Request(self.generate_page(i, response.url), self.parse_next, dont_filter=True) #Se genera la pagina y se hace un request a parse_next
