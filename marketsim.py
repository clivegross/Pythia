# A very simple, rough, hacky market simulator, utilising QSTK
# usage: execute python marketsim.py startCash input.csv ouput.csv
# startCash is a number representing starting value of investment
# input.csv is a list of orders in the form: year, month, day, symbol, 'Buy' or 'Sell', volume of shares
# input.csv is the filename for the output of the simulation in the form: year, month day, total value

# import re uired modules
import sys
import csv
import datetime as dt
import pandas as pd
import qstkutil.DataAccess as da
import qstkutil.qsdateutil as du

# read in inputs using argv
startCash = float(sys.argv[1])
inFilename = sys.argv[2]
outFilename = sys.argv[3]

# print inputs to show correct read
print "Starting cash: $" + str(startCash)
print "Input file: " + inFilename
print "Output file: " + outFilename

# initialise script variables
orders = []
symbols = []
cash = []
cash.append(startCash)
portfolio = []
value = []
total = []

# read in input csv file as list, convert elements to appropriate types
# input csv file format: 2011,1,10,AAPL,Buy,1500,
with open(inFilename, 'rU') as infile:
    reader = csv.reader(infile)
    for row in reader:
        orders.append([dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16), row[3], row[4], int(row[5])])
        # NEED TO SORT THIS LIST CHRONOLOGICALLY

# get timestamps list
startDate = min(orders)[0]
endDate = max(orders)[0]
closeTime = dt.timedelta(hours = 16) #4PM
timestamps = du.getNYSEdays(startDate, endDate, closeTime)

# get all stock symbols from orders input.csv in array
symbols = list(set([order[1] for order in orders]))

# get closing price for each date for each symbol in pandas datframe from Yahoo
dataobj = da.DataAccess('Yahoo')
close = dataobj.get_data(timestamps, symbols, "close")

# for each trading day in range
for timestamp in timestamps:
    # reset value of equities on this day to 0
    totalValue = 0
    portfolioToday = [0] * len(symbols)
    # for each symbol that has an order on this day
    for symbol in symbols:
        isOrdered = False
        for order in orders:
            value = 0
            #if there is an order for this symbol on this date:
            if timestamp.date() == order[0].date() and symbol == order[1]:
                isOrdered = True
                # value of order is close price * quantity of shares ordered
                quantity = order[3]
                price = close[symbol][timestamp]
                value = quantity*price
                # make a buy order '+' and sell order '-'
                if order[2] == "Sell": #if its a "Sell" order:
                    value = value*(-1)
                # adjust todays portfolio to include for buy or sell trades for this symbol
                portfolioToday[symbols.index(symbol)] = portfolioToday[symbols.index(symbol)] + value
                # add on to total value of orders on this day
                totalValue = totalValue + value
        # adjust todays portfolio to include growth of investments since previous trading day
        if len(portfolio) >= 1:
            valuePrevious = portfolio[len(portfolio)-1][symbols.index(symbol)]
            dayReturn = close[symbol][timestamp]/close[symbol][timestampYesterday]
            if isOrdered:
                portfolioToday[symbols.index(symbol)] = portfolioToday[symbols.index(symbol)]+valuePrevious*dayReturn
            else:
                portfolioToday[symbols.index(symbol)] = valuePrevious*dayReturn
    # add todays portfolio to portfolio array
    portfolio.append(portfolioToday)
    if timestamp == timestamps[0]:
        cash[0] = cash[0]-totalValue
    else:
        # adjust cash level for any buy or sell trades today
        cash.append(cash[len(cash)-1]-totalValue)
    timestampYesterday = timestamp

i=0
for timestamp in timestamps:
    total.append(sum(portfolio[i])+cash[i])
    if timestamp == timestamps[len(timestamps)-1]:
        print 'total at last day: ' + str(timestamp) + ' cash: $' + str(cash[i]) + ' portfolio: $' + str(sum(portfolio[i])) + ' total: $' + str(total[i])
    i=i+1

# write to output csv
i=0
with open(outFilename, 'wb') as csvfile:
    writeLine = csv.writer(csvfile, delimiter=',')
    for timestamp in timestamps:
        writeLine.writerow([timestamp.year, timestamp.month, timestamp.day, total[i]])
        i=i+1

