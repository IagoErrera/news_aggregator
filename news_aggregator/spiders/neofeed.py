import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

from datetime import datetime, timedelta, time

class NeofeedSpider(scrapy.Spider):
    name = "neofeed"
    start_urls = ["https://neofeed.com.br/negocios/"]

    def __init__(self, start_url=None, *args, **kwargs):
        super(NeofeedSpider, self).__init__(*args, **kwargs)
        
        self.date = datetime.combine(datetime.now() - timedelta(days=1), time.min)
        print(self.date)

    def err_request(self, failure):
        print("Error on Request")
        
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def parse(self, response):
        news = response.css('div.news div[class=\"row notice-block light-red no-border\"]')[0].css('article.box-news')

        for news_item in news:
            headline = news_item.css('div.inner-top h3.title-listagem::text').get()
            link = news_item.css('div.inner-top div.box-top a::attr(href)').getall()[1]
            date = news_item.css('div.inner-bottom span.date::text').get()
            date = datetime.strptime(date.replace('\r', '').replace('\n', '').strip(), '%d/%m/%y')

            if self.date != date: continue

            item = NewsItem()
            item['link'] = link
            item['headline'] = headline.replace('\r', '').replace('\n', '').strip()
            yield item


