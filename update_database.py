from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
import os


def update_database():
    """parses a webpage and updates a database"""
    try:
        configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'currency_analyzer.settings'
        sett = get_project_settings()
        runner = CrawlerRunner(settings=sett)
        d = runner.crawl('CurrencySpider')
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
    except ValueError:
        print('Value error has been raised while parsing')
