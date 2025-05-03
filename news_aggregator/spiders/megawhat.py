import scrapy

from news_aggregator.items import NewsItem

class MegawhatSpider(scrapy.Spider):
    name = "megawhat"
    start_urls = ["https://megawhat.energy/ultimas-noticias"]

    def parse(self, response):
        news = response.css('article')

        for news_item in news:
            time = news_item.css('span.feed-date').get()
            if not 'h' in time: break

            link = news_item.css('a.feed-link::attr(href)').get()
            headline = news_item.css('h2.feed-title::text').get()

            item = NewsItem()
            item["link"] = link
            item["headline"] = headline
            yield item