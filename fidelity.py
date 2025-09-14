# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:09:45 2018

@author: sgtay

"""

#from dinero.dinero2 import account
import pandas as pd
from dinero.account import account

def numconvert(x):
    if type(x) == float:
        return x
    else: #assume x is a string
        x = x.replace(",","").replace("$","")
        return float(x)

class Fidelity(account):
    def textread(self,path,accountname,header = 0):
        data = pd.read_csv(path,header = header,index_col = False).dropna(subset = ['Quantity'])

        self.ledger = pd.DataFrame(columns = ['Ticker','Qty','Price','Value'])
        self.ledger['Ticker'] = data['Symbol']
        self.ledger['Qty'] = data['Quantity']
        self.ledger['Price'] = data['Last Price'].apply(lambda x: x.replace("$","")).astype(float)
        self.ledger['Value'] = data['Current Value'].apply(numconvert)
        self.ledger= self.ledger.dropna(subset =['Value'])
        self.ledger['Account'] = accountname
        self.add_cats()

def readFidelity(path:str,accountname:str,date:str,header:int = 0) -> pd.DataFrame:
    data = pd.read_csv(path,header = header,index_col = False).dropna(subset = ['Quantity'])

    data = data.loc[data['Quantity'] != '--'].copy()

    data['Quantity'] = data['Quantity'].apply(numconvert)

    df = pd.DataFrame(columns = ['Ticker','Qty','Price'])
    df['Ticker'] = data['Symbol']
    df['Qty'] = data['Quantity']
    df['Price'] = data['Last Price'].apply(lambda x: x.replace("$","")).astype(float)
    df['Account'] = accountname
    df['Date'] = date

    return df
