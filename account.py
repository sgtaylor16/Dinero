import pandas as pd
from alpha_vantage.timeseries import TimeSeries 
import re
import time
import yfinance as yf


class account:
       
    '''Base class for financial accounts, children of this class have their own
    tailored __init__ files to scrape instituions web sites.
    '''
    def __init__(self,ledger = None):
        if ledger is None:
            self.ledger = pd.DataFrame(columns = ['Account','Cat','Price','Qty','Ticker','Value'])
        else:
            self.ledger = ledger 
    
    
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
        ('VBTIX','Bond'),('VINIX','Large Cap'),
        ('VTMGX','IntNatl'),('PLFIX','Large Cap'),
        ('ITOT','Large Cap'),('VCIT','Bond'),
        ('FNBGX','Bond'),('FSPSX','IntNatl'),
        ('SPTL','Bond'),('VBILX','Bond')]

    categories = pd.DataFrame.from_records(matrix, columns = ['Ticker','Cat']) 
       
    
    def add_cats(self):
        '''
        Adds the categories to the ledger
        '''
        self.ledger = pd.merge(self.ledger,account.categories,how = 'left', left_on='Ticker', right_on='Ticker')
    def Value(self):
        '''Returns the value of an account'''
        return self.ledger.Value.sum()
        
    def __add__(self,other):
        '''
        Operator overload for account add method that joins different
        accounts
        '''
        df = pd.concat([self.ledger,other.ledger])
        new_instance = account(df)
        return new_instance
        
    def save(self,path):
        '''
        Saves an account ledger (pandas df) as a dataframe
        '''
        out = self.ledger.to_json(orient = 'records')
        with open(path,'w') as f:
            f.write(out)
            f.close()
                       
    def read(self,path):
        '''
        Reads a json file as a dataframe
        '''
        self.ledger = pd.read_json(path,orient = 'records')
        
    def new_price(self,ticker):
        yfob = yf.Ticker(ticker)
        return yfob.history(period ='1d').iloc[-1]['Close']
           
    def refresh(self,key):
        '''
        Refreshes and account's prices, but not quantities using the 
        yfinance package
        '''
        #Pick only the funds with active tickers

            
        test = re.compile('^[A-Z]+$')  #regex to find stock tickers

        nrows,ncols = self.ledger.shape # Get shape of dataframe
        for row in range(nrows):
            if (test.match(self.ledger.loc[row,'Ticker']) is not None) and (self.ledger.loc[row,'Ticker'] != 'SWVXX'):
                print(self.ledger.loc[row,'Ticker'])
                self.ledger.loc[row,'Price'] = new_price(self.ledger.loc[row,'Ticker'])
                print(self.ledger.loc[row,'Price'])
                self.ledger.loc[row,'Value'] = self.ledger.loc[row,'Price'] * self.ledger.loc[row,'Qty']
            time.sleep(1)
                        
    def addPrin(self,qty,value):
        '''Function to manually set the value in the Principal Fund'''
        #Get Price
#        price = self.new_price('PLFIX',key)
        price = value/qty
        new_row = pd.DataFrame({'Ticker':'PLFIX','Qty':qty,'Price':price,'Value':value,'Account': 'IMMI401K','Cat':'Large Cap'},index =[1])
        self.ledger = pd.concat([self.ledger,new_row],axis = 0)