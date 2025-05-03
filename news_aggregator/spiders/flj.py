import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

from datetime import datetime, timedelta, time

class FljSpider(scrapy.Spider):
    name = "flj"
    allowed_domains = ["flj.com.br"]
    start_urls = ["https://flj.com.br/ultimas-noticias/"]

    page = 1

    def __init__(self, start_url=None, *args, **kwargs):
        super(FljSpider, self).__init__(*args, **kwargs)
        
        self.date = datetime.combine(datetime.now() - timedelta(days=1), time.min)

    def err_request(self, failure):
        print("Error on Request")
        
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def get_date(self, str):
        date = str.split(' – ')[0].split(', ')[1]
        return datetime.strptime(date, '%d/%m/%Y')

    def parse(self, response):
        try:
            news = response.css('div.archive-list-feed article.feed')

            continue_search = True
            for news_item in news:
                headline = news_item.css('h2.feed-title::text').get()
                link = news_item.css('a.feed-link::attr(href)').get()
                excert = news_item.css('p.feed-excert::text').get()

                if self.date != self.get_date(excert):
                    continue_search = False
                    break

                item = NewsItem()
                item["link"] = link
                item["headline"] = headline
                yield item

            if continue_search:
                self.page += 1
                yield scrapy.Request(
                    f"https://flj.com.br/ultimas-noticias/page/{self.page}", 
                    callback=self.parse,
                    errback=self.err_request
                )
        except Exception as e:
            print("[ERROR] ", e)
