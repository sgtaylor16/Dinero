# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:09:45 2018

@author: sgtay

"""

#from dinero.dinero2 import account
import pandas as pd
from dinero.account import account

class Fidelity(account):
     
    def textread(self,path,accountname,header = 0):
        data = pd.read_csv(path,header = header,index_col = False).dropna(subset = ['Quantity'])

        def numconvert(x):
            if type(x) == float:
                return x
            else: #assume x is a string
                x = x.replace(",","").replace("$","")
                return float(x)


        self.ledger = pd.DataFrame(columns = ['Ticker','Qty','Price','Value'])
        self.ledger['Ticker'] = data['Symbol']
        self.ledger['Qty'] = data['Quantity']
        self.ledger['Price'] = data['Last Price'].apply(lambda x: x.replace("$","")).astype(float)
        self.ledger['Value'] = data['Current Value'].apply(numconvert)
        self.ledger= self.ledger.dropna(subset =['Value'])
        self.ledger['Account'] = accountname
        self.add_cats()
