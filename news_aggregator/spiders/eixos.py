import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

from datetime import datetime, timedelta

class EixosSpider(scrapy.Spider):
    name = "eixos"
    allowed_domains = ["eixos.com.br"]
    
    page = 1 

    search_str_array = [
        "energia",
        "eletrica",
        "eletrico",
        "saneamento",
        "sabesp",
        "cemig",
        "eletrobras",
    ]

    def __init__(self, date=None, search_str=None, start_url=None, *args, **kwargs):
        super(EixosSpider, self).__init__(*args, **kwargs)
        date = datetime.now() - timedelta(days=1)
        self.date = f"{date.year}-{date.month if date.month >= 10 else f"0{date.month}"}-{date.day if date.day >= 10 else f"0{date.day}"}"
    
        if search_str: self.search_str_array = [s.lower() for s in search_str.split(',')]


    def err_request(self, failure):
        print("ERROR ON REQUEST")

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def gen_url(self, search_str):
        url = f"https://eixos.com.br/page/{self.page}/?s={search_str}&order=DESC&cat-list=0&date-start={self.date}&date-end={self.date}"
        return url

    def start_requests(self):
        for search_str in self.search_str_array:
            yield scrapy.Request(self.gen_url(search_str), callback=self.parse, errback=self.err_request)

    def parse(self, response):
        next_page = response.css('a.next::attr(href)').get()
        news = response.css('div.archive-list-feed article.feed')
        
        for news_item in news:
            headline = news_item.css('h2.feed-title::text').get()
            link = news_item.css('a.feed-link::attr(href)').get()

            item = NewsItem()
            item["link"] = link
            item["headline"] = headline
            yield item

        if next_page:
            self.page += 1
            for search_str in self.search_str_array:
                if not (search_str in response.url): continue
                
                yield scrapy.Request(self.gen_url(search_str), callback=self.parse, errback=self.err_request)
                break