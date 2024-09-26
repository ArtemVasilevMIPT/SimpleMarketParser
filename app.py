from flask import Flask, send_from_directory, request, redirect, render_template
import os
from CurrencyAnalyzer import render_query, init_dates, init_database, generate_query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

# Connection to the database
connection = None
# Current query
query = ""
# Dates to search
time_range = ['2020', '01', '07']
# Dates that exist in database
existing_dates = []
# Start search or not
start = False


@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico'
    )


@app.before_first_request
def initialize():
    global connection
    engine = create_engine('sqlite:///currency.sqlite')
    if not os.path.exists('currency'):
        declarative_base().metadata.create_all(engine)
    connection = sessionmaker(bind=engine)


@app.route('/', methods=['GET'])
def get():
    """Renders currency database"""
    global connection
    global query
    global time_range
    global start
    if start:
        return render_template('main_page.html', cells=[], time_range=time_range)
    else:
        start = False
        return render_template('main_page.html', cells=query, time_range=time_range)


@app.route('/search', methods=['POST'])
def search():
    global time_range
    global query
    global connection
    global existing_dates
    session = connection()
    time_range[0] = request.form['YearFrom']
    time_range[1] = request.form['MonthFrom']
    time_range[2] = request.form['DayFrom']
    if len(existing_dates) == 0:
        existing_dates = init_dates(session )
    query = generate_query(session, time_range, existing_dates)
    session.close()
    return redirect('/')


if __name__ == '__main__':
    app.run()
