from flask import Flask, send_from_directory, request, redirect
import os
from CurrencyAnalyzer import render_query, init_dates, init_database, generate_query

app = Flask(__name__)

# Connection to the database
connection = None
# Current query
query = ""
# Dates to search
time_range = ['2020', '01', '07']
# Dates that exist in database
existing_dates = []


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
    if not connection:
        connection = init_database(connection)
    if len(existing_dates) == 0:
        existing_dates = init_dates(connection)
    query = generate_query(time_range, existing_dates)
    return redirect('/')


if __name__ == '__main__':
    app.run()
