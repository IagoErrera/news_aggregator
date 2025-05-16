import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

import json
from urllib.parse import quote, urlencode, urlparse, parse_qs
from datetime import datetime, timedelta

class EstadaoSpider(scrapy.Spider):
    name = "estadao"
    allowed_domains = ["www.estadao.com.br"]

    size = 100
    off = 0
    base_url = 'https://www.estadao.com.br'
    d = ''

    search_str_array = [
        "energia",
        "eletrica",
        "eletrico",
        "saneamento",
        "sabesp",
        "cemig",
        "eletrobras",
    ]

    def __init__(self, search_str=None, start_url=None, *args, **kwargs):
        super(EstadaoSpider, self).__init__(*args, **kwargs)
        start_date = datetime.now() - timedelta(days=1)

        self.start_date = f'{start_date.day if (start_date.day) >= 10 else f"0{start_date.day}"}/{start_date.month if (start_date.month) >= 10 else f"0{start_date.month}"}/{start_date.year}'  
        
        # if search_str: self.search_str = search_str
        if search_str: self.search_str_array = [s.lower() for s in search_str.split(',')]


    def generate_api_url(self, search_str):
        inner_params = {
            "mode": "api",
            "size": self.size,
            "from": self.off,
            "sort": "date",
            "search_text": search_str,
            "date_range": f"{self.start_date},{self.start_date}"
        }
        inner_params_str = json.dumps(inner_params, separators=(",", ":"))

        print(inner_params_str)

        outer_query = {
            "params": inner_params_str,
            "requestUri": "/busca"
        }

        query_str = json.dumps(outer_query, separators=(",", ":"))

        print(query_str)

        url_params = {
            "query": query_str,
            "d": self.d,
            "_website": "estadao"
        }

        encoded_params = urlencode(url_params, quote_via=quote)

        print(encoded_params)

        base_url = "https://www.estadao.com.br/pf/api/v3/content/fetch/search-story"
        url = f"{base_url}?{encoded_params}"

        print(url)

        return url

    def err_request(self, failure):
        print("ERROR ON REQUEST")

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def start_requests(self):
        url = f'{self.base_url}/busca'
        yield scrapy.Request(url, callback=self.set_base_d, errback=self.err_request, meta={'force_utf8': True})

    def set_base_d(self, response):
        response = response.replace(encoding='utf-8')
        css_link = response.css('link#fusion-template-styles::attr(href)').get()

        if css_link:
            clean_url = css_link.replace('&amp;', '&')

            parsed_url = urlparse(clean_url)

            query_params = parse_qs(parsed_url.query)
        
            d_value = query_params.get('d', [None])[0]

            self.d = d_value

            for search_str in self.search_str_array:
                url = self.generate_api_url(search_str)
                yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        try:
            data = json.loads(response.text)

            for element in data["content_elements"]:
                item = NewsItem()
                item['link'] = f"{self.base_url}{element["canonical_url"]}"
                item['headline'] = element["headlines"]["basic"]
                yield item
            
            if len(data["content_elements"]) == self.size:
                self.off += self.size

                for search_str in self.search_str_array:
                    if not (search_str in response.url): continue

                    url = self.generate_api_url(search_str)                
                    yield scrapy.Request(url, callback=self.parse_api, errback=self.err_request)
                    break
                
        except Exception as e:
            print("ERROR ON PARSE API: ", response.url)
            print(e)

