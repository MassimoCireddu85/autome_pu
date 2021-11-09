import datetime
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import numpy as np

#define the current path
curr_path = str(pathlib.Path().absolute())

#future_date = datetime.today() #https://www.programiz.com/python-programming/datetime/current-datetime
future_date = datetime.datetime.now().date()
past_date = datetime.date(2000, 1, 1)

#date time difference for stock df extraction Yahoo Finance
#https://www.kite.com/python/answers/how-to-find-the-number-of-seconds-between-two-datetime-objects-in-python
difference = (future_date - past_date)
total_seconds = difference.total_seconds()
base_period = 946684800 #1st Jan 2000

#variable to get the current period in seconds compared to the base period jan 1st 2000
current_seconds = round(base_period + total_seconds) 

#stock dataframe taken by a list of nasdaq symbols, full list in nasdaq.csv. Slow subset of data is recommended 
#subset of stocks which went public before 2000 and make the symbols as a list
#create a list of stock symbols https://stackoverflow.com/questions/22341271/get-list-from-pandas-dataframe-column-or-row
stock_df =  pd.read_csv(""+curr_path+"\\Input\\nasdaq.csv")
stock_df_20 =  stock_df[stock_df['IPO Year']<=1999]
stock_sy = stock_df_20[['Symbol']]
stock_sy.reset_index(drop=True, inplace=True)
stocks = stock_sy['Symbol'].tolist()

#loop to create a full list of all stocks df
all_stocks = []
for symbols in stocks:
    link = 'https://query1.finance.yahoo.com/v7/finance/download/' + str(symbols) + '?period1=946684800&period2=' + str(current_seconds) + '&interval=1d&events=history&includeAdjustedClose=true'
    all_stocks.append(pd.read_csv(link))

#loop to calculate columns in each of the stock dataframes
#low and high are the extremes for the moving averages
low = 10 
high = 50
N = len(all_stocks)

for i in range(N):        
    #price 1 to get the open price of tomorrow in the same row
    #difference in price from today and tomorrow
    #daily return as the gain or loss compared to the close price
    #direction column depending on sign of Price diff via list of comprehension
    #moving average for 3 periods Average 3 with shift method
    #moving average over 10 days
    #moving average over 50 days
    #shares hold/buy or sell. If MA10 > MA50 Buy or Hold (strategy Long)
    #profit calculate the return in case Shares ==1
    #cumulative wealth of the total profit given the strategy
    try:
        all_stocks[i]['Price1'] = all_stocks[i]['Close'].shift(-1) 
        all_stocks[i]['Price_diff'] = all_stocks[i]['Price1'] - all_stocks[i]['Close']
        all_stocks[i]['Return'] = all_stocks[i]['Price_diff']/all_stocks[i]['Close'] 
        all_stocks[i]['Direction'] = [1 if all_stocks[i].loc[ei,'Price_diff'] > 0 else -1 for ei in all_stocks[i].index]
        all_stocks[i]['Average3'] = (all_stocks[i]['Close'] + all_stocks[i]['Close'].shift(1) + all_stocks[i]['Close'].shift(2))/3
        all_stocks[i]['MA10'] = all_stocks[i]['Close'].rolling(low).mean()
        all_stocks[i]['MA50'] = all_stocks[i]['Close'].rolling(high).mean()
        all_stocks[i]['Shares'] = [1 if all_stocks[i].loc[ei,'MA10'] > all_stocks[i].loc[ei,'MA50'] else 0 for ei in all_stocks[i].index]
        all_stocks[i]['Profit'] = [all_stocks[i].loc[ei,'Price diff'] if all_stocks[i].loc[ei,'Shares']==1 else 0 for ei in all_stocks[i].index]
        all_stocks[i]['Wealth'] = all_stocks[i]['Profit'].cumsum()
        all_stocks[i]['Stock name'] = stocks[i]    
    except:
        pass   