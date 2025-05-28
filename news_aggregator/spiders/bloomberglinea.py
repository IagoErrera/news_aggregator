import scrapy

from datetime import datetime, timedelta, time

from news_aggregator.items import NewsItem

class BloomberglineaSpider(scrapy.Spider):
    name = "bloomberglinea"
    start_urls = ['https://www.bloomberglinea.com.br/arc/outboundfeeds/news-sitemap.xml/?outputType=xml']
    iterator = "iternodes"
    itertag = "item"

    search_str_array = ["energia"]
    
    def __init__(self, search_str=None, start_url=None, *args, **kwargs):
        super(BloomberglineaSpider, self).__init__(*args, **kwargs)
        self.end_date = datetime.combine(datetime.now().replace(tzinfo=None), time.min)  
        self.start_date = datetime.combine(datetime.now().replace(tzinfo=None) - timedelta(days=1), time.min)

        if search_str: self.search_str_array = [s.lower() for s in search_str.split(',')]

    def parse(self, response):
        response.selector.register_namespace("ns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        response.selector.register_namespace("news", "http://www.google.com/schemas/sitemap-news/0.9")  
        
        links = response.xpath("//ns:url//ns:loc/text()").getall()
        pubDates = response.xpath("//ns:url//news:news//news:publication_date/text()").getall()

        for i in range(len(links)):
            pubDate = datetime.fromisoformat(pubDates[i]).replace(tzinfo=None)
            
            if (self.start_date < pubDate and pubDate < self.end_date):
                yield scrapy.Request(links[i], callback=self.parse_news)
        
    def parse_news(self, response):
        paragraphs = response.css('article p.body-paragraph::text').getall()
        paragraphs_str = ' '.join(paragraphs)

        for search_str in self.search_str_array:
            if search_str in paragraphs_str.lower():
                title = response.css('h1.hp-article-title::text').get()

                item = NewsItem()
                item["link"] = response.url
                item["headline"] = title
                yield item

                break