import os
import requests
import pygal
import webbrowser
import datetime
import platform
import csv
from flask import Flask, render_template, request

app = Flask(__name__)
app.config["DEBUG"] = True

# Function to read stock symbols from the CSV file
def read_stock_symbols():
    stock_symbols = []
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stock_symbols.append(row['Symbol'])
    return stock_symbols

def intradaily(symbol):
    return 'https://alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + symbol + '&interval=60min&apikey=K7HLGROEFZW2C06M'

def daily(symbol):
    return 'https://alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + symbol + '&outputsize=full&apikey=K7HLGROEFZW2C06M'

def weekly(symbol):
    return 'https://alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=' + symbol + '&outputsize=full&apikey=K7HLGROEFZW2C06M'

def monthly(symbol):
    return 'https://alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=' + symbol + '&outputsize=full&apikey=K7HLGROEFZW2C06M'

@app.route('/', methods=['GET', 'POST'])
def main():
    stock_symbols = read_stock_symbols()

    if request.method == 'POST':
        Stock_Symbol = request.form['Stock_Symbol']
        Chart_Type = int(request.form['Chart_Type'])
        Series_Type = int(request.form['Series_Type'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Retrieve stock data
        if Series_Type == 1:
            url = intradaily(Stock_Symbol)
        elif Series_Type == 2:
            url = daily(Stock_Symbol)
        elif Series_Type == 3:
            url = weekly(Stock_Symbol)
        elif Series_Type == 4:
            url = monthly(Stock_Symbol)

        r = requests.get(url)
        data = r.json()

        # Process stock data
        series_format = ""
        if Series_Type == 1:
            series_format = "Time Series (60min)"
        elif Series_Type == 2:
            series_format = "Time Series (Daily)"
        elif Series_Type == 3:
            series_format = "Weekly Time Series"
        elif Series_Type == 4:
            series_format = "Monthly Time Series"

        dataInRange = []
        dataSorted = []

        for x in data[series_format]:
            year, month, day = x.split('-')    
            if int(start_date.split('-')[0]) <= int(year) <= int(end_date.split('-')[0]) and \
                int(start_date.split('-')[1]) <= int(month) <= int(end_date.split('-')[1]) and \
                int(start_date.split('-')[2]) <= int(day) <= int(end_date.split('-')[2]):
                open_price = data[series_format][x]['1. open']
                high_price = data[series_format][x]['2. high']
                low_price = data[series_format][x]['3. low']
                close_price = data[series_format][x]['4. close']
                dataInRange.append([x, open_price, high_price, low_price, close_price])

        dataLength = len(dataInRange)
        for x in range(dataLength):
            dataSorted.append(dataInRange[dataLength - x - 1])

        dates = []
        open_prices = []
        high_prices = []
        low_prices = []
        close_prices = []

        for x in dataSorted:
            dates.append(x[0])
            open_prices.append(float(x[1]))
            high_prices.append(float(x[2]))
            low_prices.append(float(x[3]))
            close_prices.append(float(x[4]))

        # Render the chart
        if Chart_Type == 1:
            chart = pygal.Bar()
        elif Chart_Type == 2:
            chart = pygal.Line()

        chart.title = f'Stock Data for {Stock_Symbol}: {start_date} to {end_date}'
        chart.x_labels = map(str, dates)
        chart.add('Open', open_prices)
        chart.add('High', high_prices)
        chart.add('Low', low_prices)
        chart.add('Close', close_prices)
        chart_file_path = os.path.abspath('graphs/chart.svg')
        chart.render_to_file(chart_file_path)

        # Opening the chart file in a web browser
        webbrowser.open('file://' + chart_file_path)

    return render_template('index.html', stock_symbols=stock_symbols)

if __name__ == '__main__':
    app.run(port=5000)