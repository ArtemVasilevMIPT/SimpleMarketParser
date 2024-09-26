import scrapy


class CurrencyAnalyzerItem(scrapy.Item):
    date = scrapy.Field()
    name = scrapy.Field()
    symbol = scrapy.Field()
    market_cap = scrapy.Field()
    price = scrapy.Field()
