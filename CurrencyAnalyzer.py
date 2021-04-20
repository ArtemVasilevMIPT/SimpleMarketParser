import sqlite3
import pandas as pd
from currency_analyzer.currency_analyzer.spiders import spider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from flask import render_template
import datetime
import calendar
from scrapy.utils.log import configure_logging
import itertools


def generate_regex(date_from, date_to, ex_dates):
    try:
        d_f = datetime.date(int(date_from[0]), int(date_from[1]), int(date_from[2]))
        d_t = datetime.date(int(date_to[0]), int(date_to[1]), int(date_to[2]))
    except ValueError:
        return ""
    r = ""
    while d_f <= d_t:
        c = calendar.Calendar()
        cd = c.monthdatescalendar(d_f.year, d_f.month)
        day = d_f.day
        for week in cd:
            dt = week[6]
            if dt.day > d_t.day and d_f.month == d_t.month and d_f.year == d_t.year:
                break
            if dt.day < day:
                continue
            if not dt.strftime("%Y%m%d") in ex_dates:
                r += dt.strftime("%Y%m%d")
                r += "|"
                ex_dates += dt.strftime("%Y%m%d")
            day = dt.day
        year = d_f.year + (d_f.month + 1) // 13
        month = (d_f.month + 1) % 13
        if month == 0:
            month = 1
        d_f = datetime.date(year, month, 1)
    if len(r) != 0:
        if r[-1] == "|":
            r = r[:len(r) - 1]
    return r


def set_search_date(regex):
    """Sets parsing regex"""
    spider.CurrencySpider.set_rules(regex)


def set_search_number(new_number):
    if new_number > 0:
        spider.CurrencySpider.set_items_number(new_number)


def query_pandas(db, q="SELECT * FROM currency"):
    """returns result of query q to database db in a form of pandas dataframe"""
    return pd.read_sql_query(q, db)


def query_list(db, q="SELECT * FROM currency"):
    """returns result of query q to database db in a form of a list"""
    if q == "":
        return []
    frame = query_pandas(db, q)
    currency_list = []
    for index, item in frame.iterrows():
        currency_list.append((item['id'], item['date'], item['name'], item['symbol'],
                              item['market_cap'], item['price']))
    return currency_list


def render_query(db, q, dates):
    """renders query on the html webpage"""
    return render_template(
        'main_page.html',
        cells=query_list(db, q),
        time_range=dates
    )


def connect_database():
    """returns a connection to a database"""
    try:
        c = sqlite3.connect('./currency_analyzer/currency_analyzer/currency.sqlite')
        return c
    except Exception:
        db = open('./currency_analyzer/currency_analyzer/currency.sqlite', "w")
        db.close()
        return sqlite3.connect('./currency_analyzer/currency_analyzer/currency.sqlite')


def init_database(con):
    """initializes a database"""
    if not con:
        con = connect_database()
    return con


def init_dates(con):
    df = query_pandas(con)
    print(df.head())
    return df.date.unique()


def update_database():
    """parses a webpage and updates a database"""
    try:
        configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
        runner = CrawlerRunner()
        d = runner.crawl(spider.CurrencySpider)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
    except ValueError:
        pass


def check_date(date):
    """Checks whether date is valid"""
    try:
        d = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    except ValueError:
        return False
    return True


def generate_query(time_period, ex_date):
    """Generates query, according to the give time period"""
    r = ""
    q = ""
    if check_date(time_period[:3]) and check_date(time_period[3:]):
        r = generate_regex(time_period[:3], time_period[3:], ex_date)
    else:
        return ""
    if r != "":
        set_search_date(r)
        update_database()
    s_f = time_period[0] + '-' + time_period[1] + '-' + time_period[2]
    s_t = time_period[3] + '-' + time_period[4] + '-' + time_period[5]
    q = "SELECT * FROM currency WHERE [date] BETWEEN '" + s_f + "' AND '" + s_t + "'"
    return q
