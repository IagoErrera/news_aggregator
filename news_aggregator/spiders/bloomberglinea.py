import scrapy

import json

class BloomberglineaSpider(scrapy.Spider):
    name = "bloomberglinea"
    allowed_domains = ["www.bloomberglinea.com.br"]
    # start_urls = ["https://www.bloomberglinea.com.br/queryly-advanced-search/?query="]
    start_urls = ["https://api.queryly.com/json.aspx?queryly_key=be18f0998ba24b20&query=economia%20&endindex=20&batchsize=20&callback=searchPage.resultcallback&showfaceted=true&extendeddatafields=creator,imageresizer,promo_image,subheadline&timezoneoffset=180&sort=date"]

    search_str = ""

    # def generate_url(self):
    #     return f'https://www.bloomberglinea.com.br/queryly-advanced-search/?query={self.search_str}'

    def parse(self, response):
        print(response.text)

        data = json.loads(response.text)

        print(data)

        pass
