# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 21:22:38 2017

@author: sgtay
"""



import time
from bs4 import BeautifulSoup as bs
import pandas as pd
from dateutil.parser import parse
import datetime
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import pandas_datareader as pdr
import re
#from alpha_vantage.timeseries import TimeSeries  
import seaborn as sns
#https://github.com/RomelTorres/alpha_vantage
import time
pd.options.display.float_format = '{:,.2f}'.format


def bubble(account,key,groupkey = 'Category',days_past = 60):
    ts = TimeSeries(key = key, output_format = 'pandas')
    df = account.portfolio
    if groupkey == 'Category':
        df_columns = ['Return','Risk','Value']
        new_df = pd.DataFrame(columns = df_columns)
        catdf = df.Value.groupby([df.Cat,df.Ticker]).sum()
        #Calculate the risk (Volatility)
        for cat in catdf.index.get_level_values(0).unique().tolist():
            if (cat == 'Bond' or cat == 'Cash'):
                treturn = 0.0
                vol = 0.0
                total_value = catdf[cat].sum()
            else:
                total_value = catdf[cat].sum()  #To be used in weighted sums
                treturn = 0.0
                vol = 0.0
                for ticker in catdf[cat].index:
#                    time.sleep(15)
                    print(ticker)
                    weight = catdf[cat][ticker]/total_value
                    if ticker == 'Principal':
                        history = ts.get_daily(symbol = 'SCHX')[0].loc[:,'close']
                    else:
                        history = ts.get_daily(symbol = ticker)[0].loc[:,'close']
                    history = history.iloc[-days_past:]
                    vol = weight * Volatility(history).std() + vol
                    treturn = weight * (history.iloc[-1]/history.iloc[0])+treturn

                    
            tempdf = pd.DataFrame.from_records(data = [(treturn,vol,total_value)]
                ,columns = df_columns,index = [cat])
            new_df = new_df.append(tempdf)
            
    fig,ax = plt.subplots()
    new_df.plot.scatter(x='Return', y='Risk', s=df['Value']/100,ax = ax);
    ax.plot
        
            
    return new_df
    
        
def get_history(ticker,key,days_past=60):
    '''Returns the price history and the daily percent change
    for a ticker over the last past_days.
    '''
    ts = TimeSeries(key = key,output_format = 'pandas')
    if days_past < 100:
        price_history = ts.get_daily(symbol = ticker)[0].loc[:,'close']
    volatility_history = Volatility(price_history)
    return [price_history,volatility_history]
    
def group_get_risk(tickerlist,qtys,key,days_past=60):
    '''
    tickers_list is a list of tickes
    qtys of each ticker so that proportions can be calculated.
    returns a Series
    '''
    ts = TimeSeries(key = key, output_format = 'pandas')
    historydf = pd.DataFrame(columns = tickerlist)
    for i,ticker in enumerate(tickerlist):
        time.sleep(10)
        temp_history = get_history(ticker,key,days_past)
        historydf[ticker] = temp_history[0]*qtys[i] #Turns price into value
    total_value = historydf.sum(axis = 1)
    return Volatility(total_value)
    
def corrplot(account):
    #get the categories in a portfolio:
    port = account.portfolio
    history = pd.DataFrame()
    categories = account.portfolio.Cat.unique()
    for category in categories:
        if category == 'Bond' or category == 'Cash':
            continue
        else:
            #Get the ticker
             tickerlist = port.loc[port.Cat == category,'Ticker'].unique()
             #Get the qty's
             qty = []
             for ticker in tickerlist:
                 print(ticker)
                 qty.append(port.loc[port.Ticker == ticker,'Qty'].sum())
             history[category] = group_get_risk(tickerlist,qty,key = 'OSA1S9RNFPTFXBI9',days_past = 60)
    return history
             

def Volatility(history):
    '''Takes a numpy array or dataseries of price histories and returns the
    standard deviation of the daily price changes as percentages as a pandas
    dataseries
    '''
    if type(history) is pd.core.series.Series:    
        history_array = history.as_matrix()
    changes = np.array([])
    for i in range(history_array.shape[0])[1:]:
        changes = np.append(changes,((history[i-1] - history[i]) / history[i]))
    return pd.Series(changes) * 100
        
def balance(account,bond_fctn):
    '''Plots an accounts holdings relative to a target account with 
    bond fctn held in bonds
    '''
    total = account.portfolio.Value.sum()
    bycat = account.portfolio.Value.groupby([account.portfolio.Cat,account.portfolio.Account]).sum()
    (cat_index,acct_index) = bycat.index.levels
    new_index = pd.MultiIndex.from_product([cat_index,acct_index])
    bycat = bycat.reindex(new_index).fillna(0)
    cats = bycat.index.get_level_values(0).unique()
    ind = np.arange(len(cats))  #index for plotting
    places = bycat.index.get_level_values(1).unique()
    width = 0.35
    cm = plt.get_cmap('gist_rainbow')
 #   fig,ax = plt.subplot()

    fig,ax = plt.subplots()
#Create a stacked plot for actual allocation
    for i,cat in enumerate(cats):
        bottoms = len(cats)* [0]
        for j,place in enumerate(places):
            col = cm(1. * j/len(places))
            value = bycat.loc[cat][place]
 #           print(value)
            plt.bar(i,value,width, bottom = bottoms[i], color = col)
            bottoms[i] = bottoms[i] + value
#    Create the lengend
    legendlist =[]
    for j, place in enumerate(places):
        legendlist.append(mpatches.Patch(color = cm(1. * j/len(places)), label = place))

    plt.legend(handles = legendlist)
    plt.xticks(ind,cats)
            
    #now calculaate appropriate targets
    aimpoints = target(bond_fctn,total)
    #Check to see what other cat are required.
    tcats = aimpoints.columns.unique()
    for cat in cats:
        if cat in aimpoints.columns:
            pass
        else:
            aimpoints[cat] = 0
    aimpoints = aimpoints[cats] 
            
    #aimpoints.columns = cats
    width = -.35  
    for i,cat in enumerate(aimpoints.columns):
            value = aimpoints[cat] * total
            print(i,cat,value)
            plt.bar(i,value,width, color = 'gray')
    temp = 'Total = ' + str(total)
    plt.text(.05,.9,temp,transform=ax.transAxes,size = 15)
    
    return bycat

def cleannum(text):
    result = text.replace('\n','')  #get rid of extra lines
    result = result.replace(',','')  #get rid of commas
    result = result.replace('$','')
    result = result.replace(' ','')
    return float(result)
    
def target(per_bond,total_value = None):
    LargeCap = (1-per_bond)*.6
    IntNatl = (1-per_bond)*0.09
    EmrgMkts = (1-per_bond)*0.09
    SmallCap = (1-per_bond)*0.11
    REIT = (1-per_bond)*0.11
    target_alloc= pd.DataFrame({'Bond':per_bond,'Large Cap':LargeCap,'IntNatl':IntNatl,'Emrg Mkts':EmrgMkts,
                           'Small Cap':SmallCap,'REIT':REIT}, index = ['Share'])
    if type(total_value) == float:
        target_alloc = target_alloc.applymap(lambda x: total_value * x)
    return target_alloc
    
    

class account:
    '''Base class for financial accounts, children of this class have their own
    tailored __init__ files to scrape instituions web sites.
    '''
    matrix = [('IJR','Small Cap'),('SCHZ','Bond'),
          ('SCHB','Large Cap'),('VB','Small Cap'),
        ('VBIIX','Bond'),('VTCLX','Large Cap'),
        ('SCHD','Large Cap'),('SCHG','Large Cap'),
        ('SCHV','Large Cap'),('MDYG','Mid Cap'),
        ('NOTIX','Bond'),('JAVTX','Other'),
        ('JAMCX','Mid Cap'),('MGIAX','IntNatl'),
        ('NOSGX','Small Cap'),('NHMAX','Bond'),
        ('VETAX','Mid Cap'),('WBIGX','IntNatl'),
        ('152708CH4','Bond'),('1980367B5','Bond'),
        ('352802GK2','Bond'),('357866WA6','Bond'),
        ('358776ET5','Bond'),('442331WB6','Bond'),
        ('538130FL4','Bond'),('590252NJ7','Bond'),
        ('642526ME4','Bond'),('70914PSL7','Bond'),
        ('720362CQ3','Bond'),('897825GH2','Bond'),
        ('SWVXX','Cash'),('SCHH','REIT'),
        ('SCHE','Emrg Mkts'),('SCHF','IntNatl'),
        ('SCHX','Large Cap'),('SCHA','Small Cap'),
        ('CORE**','Cash'),('FEMKX','Emrg Mkts'),
        ('FLBAX','Bond'),('FSIVX','IntNatl'),
        ('TIP','Bond'),('FDRXX**','Cash'),
        ('FLBIX','Bond'),('FSIIX','IntNatl'),
        ('VBTIX','Bond'),('VINIX','Large Cap')
        ,('VTMGX','IntNatl'),('PLFIX','Large Cap'),
        ('ITOT','Large Cap'),('VCIT','Bond'),('SNVXX','Cash'),
        ('SPDW','IntNatl')]
    categories = pd.DataFrame.from_records(matrix, columns = ['Ticker','Cat']) 
       
    
    def add_cats(self):
        self.portfolio = pd.merge(self.portfolio,account.categories,how = 'left', 
                                  left_on='Ticker', right_on='Ticker')
                        
#        def update_values(self,date):
#        date = dt.today

        #Need to catch errors where bond is not available.t
    def Value(self):
        '''Returns the value of an account'''
        return self.portfolio.Value.sum()
        
    def __add__(self,other):
        '''
        Operator overload for account add method that joins different
        accounts
        '''
        df = pd.concat([self.portfolio,other.portfolio])
        new_instance = add_help(df)
        return new_instance
        
    def save(self,path):
        '''
        Saves an account portfolio (pandas df) as a dataframe
        '''
        out = self.portfolio.to_json(orient = 'records')
        with open(path,'w') as f:
            f.write(out)
            f.close()
                       
    def read(self,path):
        '''
        Reads a json file as a dataframe
        '''
        self.portfolio = pd.read_json(path,orient = 'records')
        
    def new_price(self,ticker,key):
        ALPHAVANTAGE_KEY = key
        ts = TimeSeries(key = ALPHAVANTAGE_KEY, output_format = 'pandas')
        data,junk = ts.get_daily(symbol = ticker)
        return data.close[-1]
           
    def refresh(self,key):
        '''
        Refreshes and account's prices, but not quantities using the 
        AlphaVantage API
        '''
        #Pick only the funds with active tickers

            
        TODAY = datetime.today()  #Get today's date.
        test = re.compile('^[A-Z]+$')  #regex to find stock tickers
#        rowselect = self.portfolio.Ticker.apply(lambda x : test.match(x) is not None).fillna(0)
#        tickers = self.portfolio.loc[rowselect,:] #Select only active tickers
#        tickers.Price  = tickers.apply(lambda row: new_price(row.Ticker), axis = 1)
#        tickers.Value = tickers.apply(lambda row: row.Ticker * row.Qty)
        nrows,ncols = self.portfolio.shape # Get shape of dataframe
        for row in range(nrows):
            if (test.match(self.portfolio.loc[row,'Ticker']) is not None) and (self.portfolio.loc[row,'Ticker'] != 'SWVXX'):
                print(self.portfolio.loc[row,'Ticker'])
                self.portfolio.loc[row,'Price'] = new_price(self.portfolio.loc[row,'Ticker'],key)
                print(self.portfolio.loc[row,'Price'])
                self.portfolio.loc[row,'Value'] = self.portfolio.loc[row,'Price'] * self.portfolio.loc[row,'Qty']
            time.sleep(3)
            
#    def compare(self,days_past):
#        for sector in self.portfolio.Cat.unique():
    
class add_help(account):
    def __init__(self,df):
        self.portfolio = df
        
#    def Allocations:():
#        amounts = self.portfolio.Value.groupby([self.portfolio.Category]).sum()
#        fig,ax = plt.subplots()
#        width = 0.35
#        rects1 = ax.bar(, men_means, width, color='r'

    
 
class Fidelity(account):
    
    def __init__(self,username,password):
        super().__init__()
        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.fidelity.com/')
        time.sleep(10)
        UsernameElement = browser.find_element_by_xpath(r'//*[@id="userId-input"]')
        UsernameElement.send_keys(username)
        time.sleep(2)
        PasswordElement = browser.find_element_by_xpath('//*[@id="password"]')
        PasswordElement.send_keys(password)
        time.sleep(2)
        SubmitButton = UsernameElement = browser.find_element_by_xpath('//*[@id="fs-login-button"]')
        SubmitButton.click()
        time.sleep(20)
        PositionsPage = browser.find_element_by_id('tab-2')
        PositionsPage.click()
        time.sleep(20)
        account_page = browser.page_source
        accountsbs = bs(account_page)
        browser.close()
        toptable = accountsbs.findAll(class_ = 'p-positions-tbody')[1]
        tablerows = toptable.findAll('tr')
        parentdf = pd.DataFrame(index = ['Qty','Price','Account'])
        
        ticker = []# 
        qty = []#
        price = []#
        value = []
        account = []#
        
        for row in tablerows:
            
            try:
                junk = row['class']
                if row['class'][0] == 'magicgrid--account-title-row':
                    account_flag = row.find(class_ ='magicgrid--account-title-text').get_text()
                elif 'normal' in row['class'][0]:
                    columns = row.findAll('td')
                    ticker.append(columns[0].findAll('span', class_='stock-symbol')[0].get_text())
                    price.append(cleannum(columns[1].findAll('span')[0].get_text()))
                    value.append(cleannum(columns[4].get_text()))
                    qty.append(cleannum(columns[5].get_text()))
                    account.append(account_flag)
            except KeyError:
                pass
        self.portfolio = pd.DataFrame({'Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})
        self.add_cats() 
    
class Fidelity2(account):
    def __init__(self,username,password):
        super().__init__()
        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.fidelity.com/')
        time.sleep(20)
        Username = browser.find_element_by_xpath('//*[@id="userId-input"]')
        Username.send_keys(username)
        time.sleep(5)
        Password = browser.find_element_by_xpath('//*[@id="password"]')
        Password.send_keys(password)
        time.sleep(20)
        submit = browser.find_element_by_xpath('//*[@id="fs-login-button"]')
        submit.click()
        time.sleep(20)
        retire = browser.find_element_by_xpath('/html/body/div[4]/div[3]/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[3]/div[5]/div[3]')
        retire.click()
        time.sleep(20)
        page2 = browser.find_element_by_link_text('Positions')  #This doesn't work
        page2.click()
        time.sleep(20)
        account_page = browser.page_source
        pagebs = bs(account_page)
        
        browser.close()
        
        table = pagebs.findAll('tbody', class_ = 'p-positions-tbody')[1]
        
        rows = table.findAll('tr',recursive = False)
        
        ticker = []
        price = []
        qty = []
        value = []
        account =[]
        
        for row in rows:
            if 'HEALTH' in row.get_text():
                break
            elif 'normal' in row['class'][0]:
                columns = row.findAll('td')
                ticker.append(columns[0].findAll('span', class_='stock-symbol')[0].get_text())
                price.append(float(columns[1].findAll('span')[0].get_text()[1:]))
                value.append(float(columns[4].get_text()[1:].replace(',','')))        
                qty.append(float(columns[5].get_text().replace(',','')))
                account.append('RR 401K')
            
                 
        account5 = pd.DataFrame({'Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})
        self.portfolio = account5
        self.add_cats() 
        
class Principal(account):
    def __init__(self,username,password,key):
        super().__init__()
        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.principal.com')
        time.sleep(20)
        pull_down = browser.find_element_by_xpath('//*[@id="principal-primary-navbar"]/div/div[2]/ul/li[2]/a')
        pull_down.click()
        time.sleep(5)
        login = browser.find_element_by_xpath('//*[@id="principal-primary-navbar"]/div/div[2]/ul/li[2]/ul/li[3]/a')
        login.click()
        time.sleep(20)
        
        user = browser.find_element_by_xpath('//*[@id="userid"]')
        user.send_keys(username)
        field2=browser.find_element_by_xpath('//*[@id="pass"]')
        field2.send_keys(password)
        submit = browser.find_element_by_xpath('//*[@id="signon"]/input[3]')
        submit.click()
        time.sleep(20)
        account_page = browser.page_source
        account_pagebs = bs(account_page)
        browser.close()
        value = cleannum(account_pagebs.findAll('span',id = 'total-balance')[0].get_text())
        price = self.new_price('PLFIX',key)      
        qty = value / price
        account6 = pd.DataFrame({'Ticker':'PLFIX','Qty':qty,'Price':price,'Value':value,'Account': 'IMMI401K'},index =[1])
        self.portfolio = account6
        self.add_cats() 


  
