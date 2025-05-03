import scrapy


class Poder360Spider(scrapy.Spider):
    name = "poder360"
    start_urls = ["https://www.poder360.com.br/?s=search"]

    search_str = ""

    def generate_url(self):
        return f"https://www.poder360.com.br/?s=search&q={self.search_str}"

    def parse(self, response):
        pass
