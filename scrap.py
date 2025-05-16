import os
from dotenv import load_dotenv

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from news_aggregator.spiders.folha import FolhaSpider
from news_aggregator.spiders.globo import GloboSpider
from news_aggregator.spiders.flj import FljSpider
from news_aggregator.spiders.exame import ExameSpider
from news_aggregator.spiders.estadao import EstadaoSpider
from news_aggregator.spiders.eixos import EixosSpider
from news_aggregator.spiders.cnn import CnnSpider
from news_aggregator.spiders.canalenergia import CanalenergiaSpider
from news_aggregator.spiders.neofeed import NeofeedSpider
from news_aggregator.spiders.megawhat import MegawhatSpider

from send_email import send_email, fix_data

if os.path.exists("data.csv"):
  os.remove("data.csv")
if os.path.exists("news.csv"):
  os.remove("news.csv")

process = CrawlerProcess(get_project_settings())
process.crawl(FolhaSpider)
process.crawl(GloboSpider)
process.crawl(FljSpider)
process.crawl(ExameSpider)
process.crawl(EstadaoSpider)
process.crawl(EixosSpider)
process.crawl(CnnSpider)
process.crawl(CanalenergiaSpider)
process.crawl(NeofeedSpider)
process.crawl(MegawhatSpider)
process.start()

load_dotenv()

PASS = os.getenv("PASS")
FROM = os.getenv("FROM")
TO = os.getenv("TO")

subject = "News Report"
body = """Here is the news from yesterday"""
filename_data = "data.csv"
filename_fixed = "news.csv"

fix_data(filename_data, filename_fixed)
send_email(FROM, TO, PASS, subject, body, filename_fixed)