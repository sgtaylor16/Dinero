# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 21:22:38 2017

@author: sgtay
"""
print('Importing')
import pandas as pd

from dateutil.parser import parse
import datetime
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import re
from alpha_vantage.timeseries import TimeSeries  
print('finished')
#https://github.com/RomelTorres/alpha_vantage

#import webdriver.chrome.options

pd.options.display.float_format = '{:,.2f}'.format

class portfolio:

    def __init__(self):
        self.ledger = pd.DataFrame(columns = ['Account','Cat','Price','Qty','Ticker','Value'])
    
    def add_account(self,account):
        self.ledger = pd.concat([self.ledger,account.ledger])

    def subtract_account(self,AccountName):
        tempdf = self.ledger.copy()
        self.ledger = tempdf.loc[tempdf['Account'] != AccountName,:]

    def Value(self):
        return self.ledger['Value'].sum()
    
    


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
                    print(ticker)
                    weight = catdf[cat][ticker]/total_value
                    if ticker == 'Principal':
                        history = ts.get_daily(symbol = 'SCHX')[0].loc[:,'4. close']
                    else:
                        history = ts.get_daily(symbol = ticker)[0].loc[:,'4. close']
                    history = history.iloc[-days_past:]
                    vol = weight * Volatility(history).std() + vol
                    treturn = weight * (history.iloc[-1]/history.iloc[0])+treturn

                    
            tempdf = pd.DataFrame.from_records(data = [(treturn,vol,total_value)]
                ,columns = df_columns,index = [cat])
            new_df = new_df.append(tempdf)
    new_df.drop(['Bond','Cash'],inplace = True)        
    fig,ax = plt.subplots(figsize = (30,30))
    new_df.plot.scatter(x='Return', y='Risk', s=new_df['Value']/8,ax = ax,alpha = .5)     
    for cat in new_df.index:
        ax.text(new_df.loc[cat,'Return'],new_df.loc[cat,'Risk'],cat,fontsize = 20)
            
    return new_df
    
        
def get_history(ticker,key,days_past=60):
    '''Returns the price history and the daily percent change
    for a ticker over the last past_days.
    '''
    ts = TimeSeries(key = key,output_format = 'pandas')
    if days_past < 100:
        price_history = ts.get_daily(symbol = ticker)[0].loc[:,'4. close']
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
        
def balance(account,bond_fctn,figsize = (10,8),conceal = False):
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

    fig,ax = plt.subplots(figsize = figsize)
    #Create a stacked plot for actual allocation
    for i,cat in enumerate(cats):
        bottoms = len(cats)* [0]
        for j,place in enumerate(places):
            col = cm(1. * j/len(places))
            value = bycat.loc[cat][place]
            ax.bar(i,value,width, bottom = bottoms[i], color = col,align = 'edge')
            bottoms[i] = bottoms[i] + value
    #Create the lengend
    legendlist =[]
    for j, place in enumerate(places):
        legendlist.append(mpatches.Patch(color = cm(1. * j/len(places)), label = place))

    ax.legend(handles = legendlist)
    plt.xticks(ind,cats)
            
    #now calculate appropriate targets
    aimpoints = target(bond_fctn,total)
    for cat in cats:
        if cat in aimpoints.index:
            pass
        else:
            aimpoints[cat] = 0
    aimpoints = aimpoints[cats] #This just reorders
            
    #aimpoints.columns = cats
    width = -.35  
    for i,cat in enumerate(aimpoints.index):
            value = aimpoints[cat]# * total
            ax.bar(i,value,width, color = 'gray',align = 'edge')
    temp = 'Total = ${0:.2f}'.format(total)
    if conceal == False:  #plot data that gives information on nominal values
        ax.text(.05,.9,temp,transform=ax.transAxes,size = 15)
    else:  # Hide data that gives information on nominal values
        ax.set_yticklabels([])
    ax.grid()

    #Creates a table that shows differences between actuals and targets by category
    mine = account.portfolio['Value'].groupby([account.portfolio['Cat']]).sum()
    targets = target(bond_fctn,account.Value())
    compare = pd.concat([mine,targets],axis = 1,sort = False)
    compare.columns = ['Actuals','Targets']
    compare = compare.fillna(0)
    compare['Difference'] = compare.apply(lambda row: row[0] - row[1],axis = 1)
    compare.loc['Totals',:] = compare.sum()



    
    return compare

def cleannum(text):
    result = text.replace('\n','')  #get rid of extra lines
    result = result.replace(',','')  #get rid of commas
    result = result.replace('$','')
    result = result.replace(' ','')
    return float(result)
    
def target(per_bond,total_value = None):
    '''Calculates the non-bond portion of target values of sectors either normalized or as a value
    relative to the total value provided in the function call
    '''
    LargeCap = (1-per_bond)*.61  #Large Cap should be 62% of Non-bond portfolio
    IntNatl = (1-per_bond)*0.05  #International Cap should be 7% of Non-bond protfolio
    EmrgMkts = (1-per_bond)*0.08 #Emerging markets should be 9% of non-bond portfolio
    SmallCap = (1-per_bond)*0.11 #Smallcap should be 11% of non-bond portfolio
    REIT = (1-per_bond)*0.11  #REIT should be 11 percent of non bond portfolio
    cash = (1 - per_bond)*.04
    target_alloc= pd.Series(data = [per_bond,LargeCap,IntNatl,EmrgMkts,SmallCap,REIT,cash],
                            index =['Bond','Large Cap','IntNatl','Emrg Mkts','Small Cap','REIT','Cash'], name = 'Share')
    
    try:
        total_value = float(total_value)
        target_alloc = target_alloc.apply(lambda x:x * total_value)
    except (TypeError, ValueError):
        pass

    return target_alloc
    
    




#TODO Create a class to track market indices

#Check out https://finance.yahoo.com/world-indices/


