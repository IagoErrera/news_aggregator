import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

from datetime import datetime, timedelta, time

class CanalenergiaSpider(scrapy.Spider):
    name = "canalenergia"
    start_urls = ["https://www.canalenergia.com.br/?s="]

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

    month_list = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }

    def __init__(self, date=None, search_str=None, start_url=None, *args, **kwargs):
        super(CanalenergiaSpider, self).__init__(*args, **kwargs)
        self.start_date = datetime.combine(datetime.now() - timedelta(days=1), time.min)
        self.end_date = datetime.combine(datetime.now(), time.min)

        if search_str: self.search_str_array = [s.lower() for s in search_str.split(',')]

    def err_request(self, failure):
        print("ERROR ON REQUEST")

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def gen_url(self, search_str):
        url = f"https://www.canalenergia.com.br/page/{self.page}?s={search_str}&post_type=noticia&category_name=0&order=DESC"
        return url

    def parse_date(self, date_str):
        split = [p for p in date_str.split(' de ')]
        day = int(split[0])
        month = self.month_list[split[1]]
        year = int(split[2])

        return datetime(day=day, month=month, year=year)

    def start_requests(self):
        for search_str in self.search_str_array: 
            yield scrapy.Request(self.gen_url(search_str), callback=self.parse, errback=self.err_request)

    def parse(self, response):
        news = response.css('ul[class=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 my-12\"] li')

        continue_search = True
        for news_item in news:
            link = news_item.css('a:not(.bg-white)::attr(href)').get()
            headline = news_item.css('p.card-title::text').get()
            
            date = news_item.css('span[class=\"uppercase font-medium text-[0.625rem] text-neutral-500\"]::text').get()
            if not date: continue
            date = self.parse_date(date)
            if not (self.start_date <= date and date < self.end_date):
                continue_search = False
                break
            
            item = NewsItem()
            item['link'] = link
            item['headline'] = headline
            yield item

        if continue_search:
            self.page += 1

            for search_str in self.search_str_array:
                if not (search_str in response.url): continue
                
                yield scrapy.Request(self.gen_url(search_str), callback=self.parse, errback=self.err_request)
                break
 