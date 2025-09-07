# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:07:30 2018

@author: sgtay
"""
import pandas as pd
from dinero.account import account

class Schwab(account):

    def textread(self,path,accountname,header = 0):
        data = pd.read_csv(path,header = header)
        dropmask = data["Symbol"].apply(lambda x: ' ' not in x)
        data = data[dropmask]

        self.ledger = pd.DataFrame(columns = ['Ticker','Qty','Price','Value'])
        self.ledger['Ticker'] = data["Symbol"]
        self.ledger["Qty"] = data["Qty (Quantity)"].apply(lambda x: x.replace(",","")).astype(float)
        self.ledger["Price"] = data["Price"].apply(lambda x: x.replace("$","")).astype(float)
        self.ledger["Value"] = data["Mkt Val (Market Value)"].apply(lambda x: x.replace(",","")).apply(lambda x: x.replace("$","")).astype(float)
        self.ledger["Account"] = accountname
        self.add_cats()


def readSchwab(path,accountname,date,header = 2):
    data = pd.read_csv(path,header = header)
    dropmask = data["Symbol"].apply(lambda x: ' ' not in x)
    data = data[dropmask]
    df = pd.DataFrame(columns = ['Ticker','Qty','Price'])
    df['Ticker'] = data["Symbol"]
    df["Qty"] = data["Qty (Quantity)"].apply(lambda x: x.replace(",","")).astype(float)
    df["Price"] = data["Price"].apply(lambda x: x.replace("$","")).astype(float)
    df["Account"] = accountname
    df["Date"] = date

    return df