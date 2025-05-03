import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from datetime import datetime, timedelta, time

from news_aggregator.items import NewsItem

class GloboSpider(scrapy.Spider):
    name = "globo"
    start_urls = ["https://valor.globo.com/sitemap/valor/news.xml", "https://oglobo.globo.com/sitemap/oglobo/news.xml", "https://pipelinevalor.globo.com/sitemap/pipelinevalor/news.xml", "https://oglobo.globo.com/blogs/lauro-jardim/"]
    iterator = "iternodes"
    itertag = "item"

    page = 1

    def __init__(self, search_str=None, start_url=None, *args, **kwargs):
        super(GloboSpider, self).__init__(*args, **kwargs)
        self.end_date = datetime.combine(datetime.now().replace(tzinfo=None), time.min)  
        self.start_date = datetime.combine(datetime.now().replace(tzinfo=None) - timedelta(days=7), time.min)

        self.search_str_array = [s.lower() for s in search_str.split(',')]

    def err_request(self, failure):
        print("Error on Request")

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def parse(self, response):
        if 'lauro-jardim' in response.url:
            titles = response.css('a.feed-post-link::text').getall()
            links = response.css('a.feed-post-link::attr(href)').getall()
            elapsed = response.css('span.feed-post-datetime::text').getall()

            continue_search = True
            for i in range(len(titles)):
                elapsedSplit = elapsed[i].split(' ')
                if (not (len(elapsedSplit) == 3 and (elapsedSplit[2] == 'hora' or elapsedSplit[2] == 'horas'))) and (elapsedSplit[0] != 'Ontem'): 
                    continue_search = False
                    continue

                item = NewsItem()
                item["headline"] = titles[i]
                item["link"] = links[i]
                yield item
            
            if continue_search:
                self.page += 1
                yield scrapy.Request(f'https://oglobo.globo.com/blogs/lauro-jardim/index/feed/pagina-{self.page}.ghtml', callback=self.parse)

            return

        response.selector.register_namespace("ns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        response.selector.register_namespace("news", "http://www.google.com/schemas/sitemap-news/0.9")

        links = response.xpath("//ns:url//ns:loc/text()").getall()
        pubDates = response.xpath("//ns:url//news:news//news:publication_date/text()").getall()
        
        for i in range(len(links)):
            pubDate = datetime.fromisoformat(pubDates[i]).replace(tzinfo=None)

            if (self.start_date < pubDate and pubDate < self.end_date):
                yield scrapy.Request(links[i], callback=self.parse_news)

    def parse_news(self, response):
        paragraphs = response.css('p.content-text__container::text, blockquote.content-blockquote::text').getall()
        paragraphs_str = ' '.join(paragraphs)

        for search_str in self.search_str_array:
            if search_str in paragraphs_str.lower():
                title = response.css('h1.content-head__title::text').get()
                
                item = NewsItem()
                item["link"] = response.url
                item["headline"] = title
                yield item

                break