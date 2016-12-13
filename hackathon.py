from flask import Flask, request, render_template
import os
import datetime


import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
#Use support vector regression
from sklearn.svm import SVR
import urllib.request, urllib.parse, urllib.error, json
app = Flask(__name__)
app.debug=True

dayDict = {0:"2016-08-30",1:"2016-08-31",2:"2016-09-01",3:"2016-09-02",4:"2016-09-06",5:"2016-09-07",6:"2016-09-08"}
#setting up all variables

money = 100000
invested_money = 0
predict = 0
day = 1
qs = []
start = 0
end = 0
Stock ={}
read = True
name = ""


@app.route('/')
def hello_world():
    #global money
    return render_template('home.html',money=money)

def buy(name,day,quantity):
    global Stock
    global money
    global invested_money
    statement = ""
    today_price = get_price(name, day)
    cost = today_price * quantity
    if cost < money:
        money = money - cost
        invested_money += cost
        check = 0
        for keys in Stock:
            if keys == name:
                Stock[name] = Stock[name] + quantity
                check = 1
        if check == 0:
            Stock[name] = quantity
        statement = "Transaction succeed"
    else:
        statement = "Insufficient money to purchase stocks"

    return statement


def sell(name,day,quantity):
    global Stock
    global money
    global invested_money
    statement = " "
    for keys in Stock:
        if keys == name:
            if Stock[name] >= quantity:
                Stock[name] = Stock[name]- quantity
                today_price = get_price(name, day)
                profit = today_price * quantity
                if invested_money < profit:
                    invested_money = 0
                else:
                    invested_money = invested_money - profit
                money = money + profit
                statement = "Sell complete"
            else:
                statemment = "Cannot sell"
    return statement


def total_money():
    return money + invested_money


def growth_money(day):
    global invested_money
    global Stock
    invested_money = 0
    for keys in Stock:
        current_value = get_price(keys, day)
        invested_money += Stock[keys] * current_value

    return invested_money

def get_data(s):
    if s == 'GOOG' or s == 'AAPL':
        start = 6
        end = 27
    else:
        start = 7
        end = 28
    dat = pd.read_csv('C:\\Users\\paolopaolo20\\Documents\\hackathon\\templates\\' + str(s) + ".csv")
    temp = dat.ix[start:end, :5]
    return temp


def get_array_day(d):
    dayTemp = d.ix[:, 0]
    tempList = []
    for i in dayTemp:
        i = i.split('-')
        # Since the date in csv file is string, split the date
        # Only take the day ignore year), and convert it into int so that we can plot it using predict_price
        i = int(i[2])
        tempList.append(i)
    df = pd.DataFrame(tempList)
    return df


def get_array_price(d1):
    priceTemp = d1.ix[:, 4]
    prices = []
    for i in priceTemp:
        prices.append(float(i))
    priceTemp1 = pd.Series(prices)
    return priceTemp1


def get_day(dayy):
    return dayDict[dayy]


def get_price(name, dayy):
    date = get_day(dayy)
    start = datetime.date(2016, 8, 1)
    end = datetime.date(2016, 9, 8)
    stock_data = pdr.DataReader(name, 'yahoo', start, end)
    return stock_data.ix[date][3]
def get_opening_price(name, dayy):
    date = get_day(dayy)
    start = datetime.date(2016, 8, 1)
    end = datetime.date(2016, 9, 8)
    stock_data = pdr.DataReader(name, 'yahoo', start, end)
    return stock_data.ix[date][0]
def get_high_price(name, dayy):
    date = get_day(dayy)
    start = datetime.date(2016, 8, 1)
    end = datetime.date(2016, 9, 8)
    stock_data = pdr.DataReader(name, 'yahoo', start, end)
    return stock_data.ix[date][1]
def get_low_price(name, dayy):
    date = get_day(dayy)
    start = datetime.date(2016, 8, 1)
    end = datetime.date(2016, 9, 8)
    stock_data = pdr.DataReader(name, 'yahoo', start, end)
    return stock_data.ix[date][2]
def get_volume(name, dayy):
    date = get_day(dayy)
    start = datetime.date(2016, 8, 1)
    end = datetime.date(2016, 9, 8)
    stock_data = pdr.DataReader(name, 'yahoo', start, end)
    return stock_data.ix[date][4]

def predicted_price(name, x):
    data = get_data(name)
    day = get_array_day(data)
    price = get_array_price(data)
    # Kernel = type of SVM, C = penalty parameter, 1e3 = 1000
    # svr_type1 = SVR(kernel = 'linear',C = 1e3)
    # polynomial type (above is linear)
    # svr_type2 = SVR(kernel = 'poly',C=1e3,degree = 3)
    # Radial basis function type
    svr_type3 = SVR(kernel='rbf', C=1e3, gamma=0.1)
    # Create a fit model (x,y)
    # svr_type1.fit(day,price)
    # svr_type2.fit(day,price)
    svr_type3.fit(day, price)
    return svr_type3.predict(x)[0]  # vr_type2.predict(x)[0]#,svr_type1.predict(x)[0]


def get_percentage(name, dayy):
    today = get_price(name, dayy)
    yesterday = get_price(name, dayy-1)
    percent = ((today - yesterday)/ yesterday) * 100
    percent_string = str(percent) + "%"
    return percent_string


def get_news(dayy,newsDict):
    i = 1
    newss = []
    for i in range(dayy,0,-1):
        for j in newsDict[i]:
            if j[0:4] == "http":
                newss.append(j)
    i += 1
    return newss

def get_headlines(dayy,newsDict):
    i = 1
    headss = []
    for i in range(dayy,0,-1):
        for j in newsDict[i]:
            if j[0:4] != "http":
                headss.append(j)
    i += 1
    return headss

@app.route('/user')
def user():
    global Stock
    return render_template('user.html', day = day,money=money,invested_money=invested_money,Stock = Stock)


@app.route('/market')
def market():
    local_price_apple = get_price("AAPL",day)
    local_price_samsung = get_price("SSU.DE", day)
    local_price_google = get_price("GOOG", day)
    percentage_apple = get_percentage("AAPL",day)
    percentage_samsung = get_percentage("SSU.DE",day)
    percentage_google = get_percentage("GOOG",day)
    return render_template('Market.html',lpa = local_price_apple, lps = local_price_samsung, lpg = local_price_google, pa = percentage_apple, ps = percentage_samsung, pg = percentage_google)


@app.route("/apple")
def apple_graphs_page():
    global day
    global name
    name = "AAPL"
    qs = plotly_plot(name, dayDict[day])
    predict = predicted_price(name, day)
    openprice = get_opening_price(name,day)
    highprice = get_high_price(name, day)
    lowprice = get_low_price(name, day)
    volume = get_volume(name,day)
    return render_template("apple.html", name=name, day=day, predict=predict, op = openprice, hp = highprice, lp = lowprice, v = volume, quotes=qs)


@app.route("/google")
def google_graphs_page():
    global day
    global name
    name = "GOOG"
    qs = plotly_plot(name, dayDict[day])
    predict = predicted_price(name, day)
    openprice = get_opening_price(name, day)
    highprice = get_high_price(name, day)
    lowprice = get_low_price(name, day)
    volume = get_volume(name, day)
    return render_template("google.html", name=name, day=day, predict=predict, op=openprice, hp=highprice, lp=lowprice,
                           v=volume, quotes=qs)

@app.route("/samsung")
def samsung_graphs_page():
    global day
    global name
    name = "SSU.DE"
    qs = plotly_plot(name, dayDict[day])
    predict = predicted_price(name, day)
    openprice = get_opening_price(name, day)
    highprice = get_high_price(name, day)
    lowprice = get_low_price(name, day)
    volume = get_volume(name, day)
    return render_template("samsung.html", name=name, day=day, predict=predict, op=openprice, hp=highprice, lp=lowprice,
                           v=volume, quotes=qs)


def fetch_quotes(symbol, start_date, end_date):
    base_url = 'http://query.yahooapis.com/v1/public/yql'
    yql = ('select * from yahoo.finance.historicaldata where symbol = "' + symbol
           + '" and startDate = "' + start_date
           + '" and endDate = "' + end_date + '"')
    req_url = (base_url + '?q=' + urllib.parse.quote(yql)
               + '&env=http%3A%2F%2Fdatatables.org%2Falltables.env&format=json')
    try:
        response = urllib.request.urlopen(req_url)
        results = json.loads(response.read().decode('utf-8'))['query']['results']
        if results:
            return results['quote']
        else:
            return None
    except urllib.error.HTTPError:
        return None


def plotly_plot(name, end_date):
    # end_date is dayDict[day]
    qs = fetch_quotes(name, '2016-08-23', end_date)
    return qs

def read_file():
    with open('C:\\Users\\paolopaolo20\\Desktop\\newsdoc.txt', 'r') as infile:
        ins = infile.readlines()
        global news_Dict
        news_Dict = {}
        i = 0
        x = []
        for line in ins:
            cleanedLine = line.strip()
            if len(cleanedLine)==4:
                i += 1
                x = []
            else:
                #print(cleanedLine)
                x.append(cleanedLine)
                news_Dict[i] = x

@app.route('/advance')
def advance_day():
    global day
    statement = ""
    if day == 6:
        statement = "You have completed the trading game, let's see how you did!"
        return render_template('final.html', day=day, statement = statement,total=total_money())
    day = day + 1
    invested_money=growth_money(day)
    return render_template('user.html', day=day,money=money,invested_money=invested_money,Stock = Stock)

@app.route('/news')
def news():
    global read
    if read:
        read_file()
        read = False
    all_news = get_news(day, news_Dict)
    all_heads = get_headlines(day, news_Dict)
    length = len(all_news)
    return render_template('News.html',news=all_news, heads = all_heads, length = length)

@app.route('/buy')
def buy_ht():
    quantity =int(request.args['quantity'])
    global name
    print(2)
    global day
    global money
    global invested_money
    global Stock
    statement = buy(name,day,quantity)
    print(statement)
    return render_template("user.html",day=day,money=money,invested_money=invested_money, Stock = Stock,statement=statement)

@app.route('/sell')
def sell_ht():
    quantity =int(request.args['quantity'])
    print(2)
    global name
    global day
    global money
    global invested_money
    global Stock

    statement = sell(name,day,quantity)
    print(statement)
    return render_template("user.html",day=day,money=money,invested_money=invested_money,Stock = Stock,statement=statement)

if __name__ == '__main__':
    app.run()
