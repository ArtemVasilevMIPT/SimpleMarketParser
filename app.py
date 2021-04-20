from flask import Flask, send_from_directory, request, redirect
import os
from CurrencyAnalyzer import *


app = Flask(__name__)

# Connection to the database
connection = None
# Current query
query = ""
# Dates to search
time_range = ['2020', '01', '07', '2021', '01', '03']
# Dates that exist in database
existing_dates = None


@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico'
    )


@app.route('/', methods=['GET'])
def get():
    """Renders currency database"""
    global connection
    global query
    global time_range
    return render_query(connection, query, time_range)


@app.route('/search', methods=['POST'])
def search():
    global time_range
    global query
    global connection
    global existing_dates
    time_range[0] = request.form['YearFrom']
    time_range[1] = request.form['MonthFrom']
    time_range[2] = request.form['DayFrom']
    time_range[3] = request.form['YearTo']
    time_range[4] = request.form['MonthTo']
    time_range[5] = request.form['DayTo']
    if not connection:
        connection = init_database(connection)
    if not existing_dates:
        existing_dates = init_dates(connection)
    query = generate_query(time_range, existing_dates)
    return redirect('/')


if __name__ == '__main__':
    app.run()
