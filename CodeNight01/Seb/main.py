# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 17:57:15 2018

@author: Sebastian
"""

import wikipedia #for python wiki api
import requests #for the pageview api
import ast #for converting string dict to dict
import matplotlib.pyplot as plt #for graph plotting
import datetime
import quandl # for financial data
import pandas as pd #for the financial data output

quandl_api_key = 'did you really think I\'d give you my key like that'
quandl.ApiConfig.api_key = quandl_api_key

#%% Define functions
#### returns a zipped list of FTSE100 codes and names
def FTSE100_list(filename):
    ## pulled a FTSE 100 company list from google, saved it as a csv
    file_data = []
    file = open(filename, 'r') 
    for line in file:
        file_data.append(line)
    file_data = [i.split(',') for i in file_data]
    
    FTSE100_names = [i[0] for i in file_data]
    FTSE100_codes = [i[1] for i in file_data]
    FTSE100 = list(zip(FTSE100_codes,FTSE100_names))
    # just me coming up with a hacked fast solution to problem of some bad codes
    for index,value in enumerate(FTSE100):
        if '.' or '"' in value[0]:
            FTSE100.pop(index)
    return FTSE100

#### returns information about page views in the form of a dictionary
def return_page_dict(page_name, date_start, date_end):
    # Takes the date format YYYYMMDD00
    string = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/'
    string = string + page_name + '/daily/' + date_start + '/' + date_end
    print("Page requesting:: ", string)
    response = requests.get(string)
    response = response.content
    response = response.decode("utf-8")
    response = ast.literal_eval(response)
    return response["items"]

#### returns stock_name, datetime, pageviews as a lsit
def return_list_pageviews(wiki_page_name, date_start, date_end):
    # takes date format YYYYMMDD00
    response = return_page_dict(wiki_page_name, date_start, date_end)
    name = [response[index]["article"] for index,name in enumerate(response)]
    timestamp = [response[index]["timestamp"] for index,name in enumerate(response)]
    pageviews = [response[index]["views"] for index,name in enumerate(response)]
    response_return = list(zip(name,timestamp,pageviews))
    return response_return
    
#### returns historical financial data on a daily tick between two dates
def generate_fin_data(ticker_list, start_date, end_date):
    # date format YYYY-MM-DD
    # ticker, date, adj_close
    data = quandl.get_table('WIKI/PRICES', ticker = ticker_list, 
                            qopts = { 'columns': ['ticker', 'date', 'adj_close'] }, 
                            #date = { 'gte': '2015-12-31', 'lte': '2016-12-31' }, 
                            date = { 'gte': str(start_date), 'lte': str(end_date) }, 
                            paginate=True)
    data.head()
    stock_ticker = data['ticker'].tolist()
    stock_days = data['date'].tolist()
    stock_days = [i.to_pydatetime().date() for i in stock_days] #convert timestamp to date, then remove time, leaving only date
    stock_days = list(reversed(stock_days))
    stock_prices = data['adj_close'].tolist()
    stock_info = list(zip( stock_ticker, stock_days , stock_prices ))
    return data, stock_info

### takes in the return from return_list_pageviews as well as a list of trading dates in wiki date format 
def trading_days_in_wiki_response(wiki_response, trading_days_as_wiki_dates_):
    new_list = []
    for index,value in enumerate(wiki_response):
        if value[1] not in trading_days_as_wiki_dates:
            pass
        else:
            new_list.append(value)
    return new_list

#### Returns date in wiki format
def wiki_date(year, month, day):
    return str(year) + str(month).zfill(2) + str(day).zfill(2) + '00'
#### Returns date in the quandl format needed
def quandl_date(year,month,day):
    return str(year)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)


#%%
#test the functions
return_page_dict_test = return_page_dict('Standard Chartered', '2017090100', '2017103000')
return_list_pageviews_test = return_list_pageviews("Standard Chartered", '2017090100', '2017103000')
generate_fin_data_test1, generate_fin_data_test2 = generate_fin_data(['AAPL'], '2017-09-01','2017-10-30')
FTSE100 = FTSE100_list("FTSE100Companies.csv")

#%%
### learning how to use a REST api with python
### Messing around with the wikipedia api (import wikipedia)
test_req = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/Albert_Einstein/daily/2015100100/2015103100'
test_response = requests.get(test_req)
#print(test_response.status_code)
#print(test_response.content)
test_content = test_response.content #this is in bytes
test_content = test_content.decode("utf-8") #convert to a string
# still a string representation of a dictionary
test_content = ast.literal_eval(test_content) # convert to dictionary

#%%
##### set dates
# must start from 2017 for the financial info (can't return this year's info)
start_year = 2017
start_month = 9
start_day = 1
end_year = 2017
end_month = 10
end_day = 30
#str(1).zfill(2) ### converts e.g. '1' to '01'

start_date = datetime.date(start_year, start_month, start_day)
end_date = datetime.date(end_year, end_month, end_day)
date_range = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]
delta = end_date - start_date #number of days in range
#print(delta.days)

#%% plot pageviews for a single company
plt.title(return_list_pageviews_test[0][0])
plt.xlabel('days')
plt.ylabel('pageviews')
plt.plot(range(0,delta.days+1), [i[2] for i in return_list_pageviews_test])
plt.show()

#%%
# plot pageviews for several companies
legend_names = []; legend_codes = []
for i in range(0,40,8):
    FTSE_name = FTSE100[i][1]
    FTSE_code = FTSE100[i][0]
    legend_names.append(FTSE_name)
    legend_codes.append(FTSE_code)
    response = return_list_pageviews(FTSE_name, 
                                     wiki_date(start_year, start_month, start_day), 
                                     wiki_date(end_year, end_month, end_day))
    plt.plot(range(0,delta.days+1), [i[2] for i in response])
plt.legend(legend_names)
plt.show()

#%%
#### get historic financial data for several companies
raw_data, data = generate_fin_data(legend_codes, 
                                   quandl_date(start_year, start_month, start_day), 
                                   quandl_date(end_year, end_month, end_day))

#%% Now we want to get only the pageviews that correspond to trading days from the financial data
# convert the datetime to a wiki appropriate date i.e. datetime to YYYYMMDD00
trading_days = list(set([i[1] for i in data]))
trading_days_as_wiki_dates = [i.strftime('%Y%m%d')+'00' for i in trading_days]



trading_wiki_response = trading_days_in_wiki_response(return_list_pageviews_test,
                                                      trading_days_as_wiki_dates)

#%%        
# now plot pageviews for trading days only and see what we get
plt.title(return_list_pageviews_test[0][0])
plt.xlabel('days')
plt.ylabel('pageviews')
plt.plot(range(0,len(return_list_pageviews_test)), [i[2] for i in return_list_pageviews_test])
plt.show()

#%%
def wikiAPI_response_business_days(wikiAPI_response, stock_days):
    ### returns a list of the pageviews only relating to certain business days
    # convert the stock_days generated to a format that can be cross-checked with the wikipedia api return
    business_days = [i.strftime('%Y%m%d')+'00' for i in stock_days]
    validated_list = []
    for i in wikiAPI_response:
        if i['timestamp'] in business_days:
            validated_list.append(i)
    return validated_list

#%%
### quickly hack together a historic stock price plot
temp_list = []
for i in data:
    if i[0] == 'III':
        temp_list.append(i)
plt.title('3i company')
plt.xlabel('days')
plt.ylabel('stock price')
plt.plot(range(0,len(temp_list)), [i[2] for i in temp_list])
plt.show()

### get that pageview thing as well
