import os, logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
from scrapy.exceptions import DropItem
from scrapy import signals
from currency_analyzer.items import CurrencyAnalyzerItem
import pandas as pd
from collections import Counter

logger = logging.getLogger(__name__)

DeclarativeBase = declarative_base()


class Currency(DeclarativeBase):
    __tablename__ = 'currency'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column('id', Integer, primary_key=True)
    date = Column('date', Date)
    name = Column('name', String)
    symbol = Column('symbol', String)
    market_cap = Column('market_cap', String)
    price = Column('price', String)

    def __init__(self, item):
        self.date = pd.to_datetime(item['date'], format='%Y%m%d')
        self.name = item['name']
        self.symbol = item['symbol']
        self.market_cap = item['market_cap']
        self.price = item['price']

    def __repr__(self):
        return "<Currency({0}, {1}, {2})>".format(self.id, self.symbol, self.market_cap)


class CurrencyAnalyzerPipeline(object):
    def __init__(self, settings):
        self.database = settings.get('DATABASE')
        self.engine = create_engine(URL(**self.database), poolclass=NullPool, echo=False)
        if not os.path.exists('currency'):
            DeclarativeBase.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        crawler.signals.connect(pipeline.close_spider, signals.spider_closed)
        crawler.signals.connect(pipeline.open_spider, signals.spider_opened)
        return pipeline

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        session = self.session()
        currency = Currency(item)

        try:
            session.add(currency)
            session.commit()
            logger.info('Item {} stored in db'.format(currency))
        except Exception as e:
            logger.info('Failed to add {} to db'.format(currency))
            session.rollback()
            raise e
        finally:
            session.close()

        return item
