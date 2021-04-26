import sqlite3
import pandas as pd
from currency_analyzer.spiders import spider
from flask import render_template
import datetime
import calendar
from update_database import update_database


def get_closest_date(d):
    c = calendar.Calendar()
    cd = c.monthdatescalendar(d.year, d.month)
    dt = None
    for week in cd:
        if week[6].day > d.day:
            dt = week[6]
            break
    if not dt:
        m = d.month + 1
        if m > 12:
            cd = c.monthdatescalendar(d.year + 1, 1)
        else:
            cd = c.monthdatescalendar(d.year, m)
        for week in cd:
            if week[6].day > d.day:
                dt = week[6]
                break
    return dt


def generate_regex(date_from, ex_dates):
    try:
        d = datetime.date(int(date_from[0]), int(date_from[1]), int(date_from[2]))
    except ValueError:
        return ""
    dt = get_closest_date(d)
    if dt.strftime("%Y%m%d") in ex_dates:
        return ""
    else:
        ex_dates += [dt.strftime("%Y%m%d")]
        return dt.strftime("%Y%m%d")


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
    c = sqlite3.connect('currency.sqlite')
    return c


def init_database(con):
    """initializes a database"""
    if not con:
        con = connect_database()
    return con


def init_dates(con):
    df = query_pandas(con)
    res = df.date.unique()
    for i in range(len(res)):
        res[i] = ''.join(res[i].split('-'))
    return res


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
    if check_date(time_period):
        r = generate_regex(time_period, ex_date)
    else:
        return ""
    if r != "":
        set_search_date(r)
        update_database()
    s_f = get_closest_date(datetime.date(int(time_period[0]), int(time_period[1]), int(time_period[2])))
    s = "'"
    s += s_f.strftime('%Y-%m-%d')
    s += "'"
    q = "SELECT * FROM currency WHERE [date] == " + s
    return q
