import scrapy

from datetime import datetime, timedelta, time

from news_aggregator.items import NewsItem

class EmSpider(scrapy.Spider):
    name = "em"
    allowed_domains = ["www.em.com.br"]
    start_urls = ["https://www.em.com.br/busca/cemig/"]

    date = datetime.combine(datetime.now().replace(tzinfo=None) - timedelta(days=1), time.min)
    page = 1

    def parse(self, response):
        print("PARSE")

        news = response.css('div#search-results-item div.news-box')

        counter = 0
        for news_item in news:
            try:
                date = news_item.css('small.d-block.txt-gray::text').get()
                date = date.replace('\n','').replace('\r','').split(' - ')[0].strip()
                date = datetime.strptime(date, "%d/%m/%Y")

                if date != self.date: continue

                counter += 1 
                title = news_item.css('div.col-sm-8.col-xs-8.mb-10 p.h4.txt-serif.mt-0.mb-10 a.txt-gray-base::attr(title)').get()
                link = news_item.css('div.col-sm-8.col-xs-8.mb-10 p.h4.txt-serif.mt-0.mb-10 a.txt-gray-base::attr(href)').get()

                item = NewsItem()
                item["link"] = link
                item["headline"] = title
                yield item

            except Exception as e:
                print("ERROR ON PARSE")
                print(e)
                continue

        if counter < 10: return
        
        self.page += 1

        yield scrapy.Request(f"https://www.em.com.br/busca/cemig/page/{self.page}", callback=self.parse)