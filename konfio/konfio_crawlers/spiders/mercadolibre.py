import re
from konfio_crawlers.items import GeneralItem
from scrapy import Spider, Request
import json
import math
import requests

__author__ = 'kgarcia'


def clean_text(x):
    x = re.sub(r'(^\s+)|(\s+$)|(  +)|(\r)|({ +})', '', ''.join(x.strip())) if x else x
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

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse, dont_filter=True)

    def parse_anuncio(self,response):
        item = GeneralItem()
        item["id_item"] = response.meta.get('deltafetch_key')

        r = requests.get("https://api.mercadolibre.com/items/"+response.meta.get('deltafetch_key').replace("-",""))
        melijson = json.loads(r.text)

        item['title'] = melijson.get("title").replace("'","")
        price = melijson.get("price")
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

        if response.xpath('//div[@class="vip-description-container"]//text()').extract():
            descripcion = ""
            for desc in response.xpath('//div[@class="vip-description-container"]//text()').extract():
                if "<img" not in desc:
                    descripcion =descripcion + "\n" + desc
            description= clean_text(descripcion)
        else:
            description = response.xpath('//pre[@class="preformated-text"]/text()').extract_first()

        if description:
            item['description'] = description.replace("'","")
        item['site'] = 'mercadolibre'

        yield item

    @staticmethod
    def generate_page(ith, url_aux):
        return re.sub('_Price', '_Desde_' + str(((ith-1 )* 48) + 1)+'_Price', url_aux)

    @staticmethod
    def get_n(response):
        try:
            n_str = response.xpath('//div[@class="quantity-results"]/text()').extract_first()
            if n_str:
                n_str = re.search('(.*) resultado', n_str).group(1).replace(',', '')
                return int(math.ceil(int(n_str)/ 48.0))
            else:
                return 1
        except:
            print '\n\nError: El XPATH cambio y no saco nada en el get_n\n\n'
            return 1

    def parse_next(self, response):
        urls = response.xpath('//a[@class="item-link item__js-link"]/@href').extract()
        if urls:
            for url in urls:
                id_inmueble = re.search(r'MLM-\d{9}', url)
                if id_inmueble:
                    id_inmueble = id_inmueble.group(0)
                    yield Request(url, self.parse_anuncio, dont_filter=True, meta={'deltafetch_key': id_inmueble})

    def parse(self, response):
        rangos = ["_PriceRange_0-100000",
                  "_PriceRange_100000-200000",
                  "_PriceRange_200000-300000",
                  "_PriceRange_300000-400000",
                  "_PriceRange_400000-1000000",
                  "_PriceRange_1000000-2000000",
                  "_PriceRange_2000000-3000000",
                  "_PriceRange_3000000-4000000",
                  "_PriceRange_4000000-7000000",
                  "_PriceRange_15000000-0"]
        tipos = response.xpath('//dl[@id="id_9991459-AMLM_1459_1"]//a/@href').extract()
        for tipo_url in tipos:
            if tipo_url != '#':
                for rango in rangos:
                    yield Request(tipo_url+rango, self.parse2, dont_filter=True)

    def parse2(self, response):
        for i in range(1, self.get_n(response) + 1):
            yield Request(self.generate_page(i, response.url), self.parse_next, dont_filter=True)
