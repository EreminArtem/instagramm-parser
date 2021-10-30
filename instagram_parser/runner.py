from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram_parser import settings
from instagram_parser.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)

    process.start()
