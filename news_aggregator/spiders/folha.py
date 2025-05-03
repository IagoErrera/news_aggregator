import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from news_aggregator.items import NewsItem

# Add https://www1.folha.uol.com.br/mercado/#90

class FolhaSpider(scrapy.Spider):
    name = "folha"

    page = 1
    month_list = {
        'janeiro': 1,
        'fevereiro': 2,
        'março': 3,
        'abril': 4,
        'maio': 5,
        'junho': 6,
        'julho': 7,
        'agosto': 8,
        'setembro': 9,
        'outubro': 10,
        'novembro': 11,
        'dezembro': 12,
        'jan': 1,
        'fev': 2,
        'mar': 3,
        'abr': 4,
        'maio': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8,
        'set': 9,
        'out': 10,
        'nov': 11,
        'dez': 12
    }

    links_list = []

    def __init__(self, start_date=None, end_date=None, search_str=None, start_url=None, *args, **kwargs):
        super(FolhaSpider, self).__init__(*args, **kwargs)

        if search_str: self.search_str = search_str

    def generate_url(self):
        url = f'https://search.folha.uol.com.br/search?q={self.search_str}&periodo=24&sd=&sd=&ed=&ed=&site=todos'
        return url

    def err_request(self, failure):
        print("Error on Request")
        
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    def start_requests(self):
        yield scrapy.Request(self.generate_url(), callback=self.parse, errback=self.err_request)
        yield scrapy.Request('https://www1.folha.uol.com.br/mercado/#100', callback=self.parse, errback=self.err_request)
        
    def parse(self, response):
        news = []
        if 'https://www1.folha.uol.com.br/mercado' in response.url:
            news = response.css('div.c-newslist div.c-headline__content a')
        else:
            news = response.css('div.c-headline__content a')
        page_navigator = response.css('li.c-pagination__arrow a::attr(href)').getall()

        for news_item in news:  
            try:
                item = NewsItem()
                item["link"] = news_item.css('::attr(href)').get()
                item["headline"] = news_item.css('h2.c-headline__title::text').get().replace('\n', '').replace('\r', '').strip()
                
                if item["link"] in self.links_list: continue
                self.links_list.append(item['link'])

                yield item
            except Exception as e:
                print(e)

        if page_navigator:
            if self.page == 1:
                self.page += 1
                yield scrapy.Request(page_navigator[0], callback=self.parse, errback=self.err_request)
            elif len(page_navigator) == 2:
                yield scrapy.Request(page_navigator[1], callback=self.parse, errback=self.err_request)