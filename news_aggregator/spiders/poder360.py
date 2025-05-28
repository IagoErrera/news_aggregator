import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_playwright.page import PageMethod

from news_aggregator.items import NewsItem

class Poder360Spider(scrapy.Spider):
    name = "poder360"
    
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    }

    search_str = "energia"
    page = 1

    def start_requests(self):
        yield scrapy.Request(
            url=self.generate_url(), 
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "a.gs-title"),
                ]
            },
            dont_filter=True, 
            callback=self.parse);

    def generate_url(self):
        return f"https://www.poder360.com.br/?s=search&q={self.search_str}"

    def err_request(self, failure):
        print("Error on Request")
        
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

    async def parse(self, response):
        news = response.css("div.gsc-expansionArea div.gsc-result")

        print("News Count: ", len(news))

        counter = 0
        for news_item in news:
            snippet = news_item.css('div.gs-bidi-start-align.gs-snippet::text').get().strip()

            print(snippet)
            if not (("horas" in snippet) or ("minutos" in snippet) or (snippet == "há 1 dia")): 
                print("Deny")
                continue; 
            
            print("Include")
            counter += 1

            title = news_item.css('a.gs-title::text').get()
            link = news_item.css('a.gs-title::attr(href)').get()

            item = NewsItem()
            item['link'] = link
            item['headline'] = title
            yield item

        if counter == 0: return

        self.page += 1

        yield scrapy.Request(
            url=self.generate_url(), 
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("click", f"div[aria-label=\"Página {self.page}\"]"),   
                    PageMethod("wait_for_selector", "a.gs-title"),
                    PageMethod("wait_for_timeout", 3000)
                ]
            }, 
            dont_filter=True,
            callback=self.parse);
