import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

from datetime import datetime, timedelta, time

class CnnSpider(scrapy.Spider):
    name = "cnn"
    start_urls = ["https://www.cnnbrasil.com.br/?s=fiscal"]

    page = 1
    search_str = ""

    def __init__(self, date=None, search_str=None, start_url=None, *args, **kwargs):
        super(CnnSpider, self).__init__(*args, **kwargs)
        if search_str: self.search_str = search_str
        self.start_date = datetime.combine(datetime.now() - timedelta(days=1), time.min)
        self.end_date = datetime.combine(datetime.now(), time.min)

    def err_request(self, failure):
        print("ERROR ON REQUEST")

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def gen_url(self):
        url = f"https://www.cnnbrasil.com.br/pagina/{self.page}/?s={self.search_str}&orderby=date&order=desc"
        print(url)
        return url

    def parse_date(self, date_str):
        date = date_str.split(' às ')[0]
        split = [p for p in date.split('/')]
        day = int(split[0])
        month = int(split[1])
        year = int(split[2])

        return datetime(day=day, month=month, year=year)

    def start_requests(self):
        yield scrapy.Request(self.gen_url(), callback=self.parse, errback=self.err_request)

    def parse(self, response):
        news = response.css('ul.home__new li.home__list__item')

        print(news)

        continue_search = True
        for news_item in news:
            link = news_item.css('a.home__list__tag::attr(href)').get()
            headline = news_item.css('h3.news-item-header__title::text').get()
            
            date = news_item.css('span.home__title__date::text').get()
            if not date: continue
            date = self.parse_date(date.strip())
            if date > self.end_date: continue
            if not (self.start_date <= date):
                print("Stop")
                print(date)
                continue_search = False
                break
            
            item = NewsItem()
            item['link'] = link
            item['headline'] = headline
            yield item

        if continue_search:
            self.page += 1
            yield scrapy.Request(self.gen_url(), callback=self.parse, errback=self.err_request)
 
