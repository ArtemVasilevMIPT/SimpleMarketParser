from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader.processors import Join
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from currency_analyzer.currency_analyzer.items import CurrencyAnalyzerItem


class CurrencyLoader(ItemLoader):
    pass


class CurrencySpider(CrawlSpider):
    name = 'CurrencySpider'
    allowed_domains = ['coinmarketcap.com']
    start_urls = ['https://coinmarketcap.com/historical/']
    items_number = 100
    regex = ""

    rules = (
        Rule(LinkExtractor(allow=('/202104[0-9]{2}', )), callback='parse_data', follow=False),
    )

    @classmethod
    def set_rules(cls, regex):
        cls.regex = regex
        cls.rules = (
            Rule(LinkExtractor(allow=(regex, )), callback='parse_data', follow=False),
        )

    @classmethod
    def set_items_number(cls, new_number: int):
        cls.items_number = new_number

    def parse_data(self, response):
        sel = Selector(response)
        items_html = sel.xpath('//table//tr')
        items = []
        item_names = items_html.xpath(
            '//td[@class="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__name"]//div//a/text()').extract()
        item_symbols = items_html.xpath(
            '//td[@class="cmc-table__cell cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__symbol"]//div/text()').extract()
        item_caps = items_html.xpath(
            '//td[@class="cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__market-cap"]//p/text()').extract()
        item_prices = items_html.xpath(
            '//td[@class="cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__price"]//a/text()').extract()
        print(response.request.url)
        for i in range(min(self.items_number, len(item_names))):
            item = CurrencyAnalyzerItem()
            item['date'] = response.request.url.split('/')[-2]
            item['name'] = item_names[i]
            item['symbol'] = item_symbols[i]
            item['market_cap'] = item_caps[i]
            item['price'] = item_prices[i]

            yield item
