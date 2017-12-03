# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 21:22:38 2017

@author: sgtay
"""


from selenium import webdriver
import selenium.webdriver.common.action_chains as A_C
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import dateutil.parser as parse
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
#import pandas-datareader as pdr

chromium_path = r'C:/Users/sgtay/Anaconda2/Scripts/chromedriver.exe'


def balance(account,bond_fctn):
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


#Create a stacked plot for actual allocation
    for i,cat in enumerate(cats):
        bottoms = len(cats)* [0]
        for j,place in enumerate(places):
            col = cm(1. * j/len(places))
            value = bycat.loc[cat][place]
 #           print(value)
            plt.bar(i,value,width, bottom = bottoms[i], color = col)
            bottoms[i] = bottoms[i] + value
    plt.xticks(ind,cats)
            
    #now calculaate appropriate targets
    aimpoints = target(0.25,total)
    #Check to see what other cat are required.
    tcats = aimpoints.columns.unique()
    for cat in cats:
        if cat in aimpoints.columns:
            pass
        else:
            aimpoints[cat] = 0
    print(aimpoints)
    aimpoints = aimpoints[cats]
            
    #aimpoints.columns = cats
    width = -.35  
    print('***')
    print(aimpoints)
    for i,cat in enumerate(aimpoints.columns):
            value = aimpoints[cat]
            print(i,cat,value)
            plt.bar(i,value,width, color = 'gray')

    
    
    print(cats)
    print(aimpoints.columns)
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
    matrix = [('IJR','Small Cap'),('SCHZ','Small Cap'),
          ('SCHB','Bond'),('VB','Small Cap'),
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
        ('CORE**','Cash'),('FEMKX','IntNatl'),
        ('FLBAX','Bond'),('FSIVX','IntNatl'),
        ('TIP','Bond'),('FDRXX**','Cash'),
        ('FLBIX','Bond'),('FSIIX','IntNatl'),
        ('VBTIX','Bond'),('VINIX','Large Cap')
        ,('VTMGX','Large Cap')]
    categories = pd.DataFrame.from_records(matrix, columns = ['Ticker','Cat']) 
       
    
    def add_cats(self):
        self.portfolio = pd.merge(self.portfolio,account.categories,how = 'left', 
                                  left_on='Ticker', right_on='Ticker')
                        
#        def update_values(self,date):
#        date = dt.today
    def new_price(self,ticker):
        asset = Share(ticker)
        new_price = asset.get_price()
        self.portfolio = self.portfolio.Price.applymap(lambda row:new_price(self.portfolio.Ticker),axis = 1)
        self.portfolio = self.portfolio.Value.applymap(lambda row: self.portfolio.Price*self.portfolio.Qty)
        self.portfolio = self.portfolio
        #Need to catch errors where bond is not available.t
    def Value(self):
        return self.portfolio.Value.sum()
        
    def __add__(self,other):
        print(self.portfolio)
        df = pd.concat([self.portfolio,other.portfolio])
        new_instance = add_help(df)
        return new_instance
        
    def save(self,path):
        out = self.to_json(orient = 'records')
        with open(path,'w') as f:
            f.write(out)
            f.close()
            
            
    def read(self,path):
        infile = pd.read_json(path,orient = 'records')
        with open(path,'r') as f:
            f.read(infile)
            f.close()
        
        
    
    
class add_help(account):
    def __init__(self,df):
        self.portfolio = df
        
#    def Allocations:():
#        amounts = self.portfolio.Value.groupby([self.portfolio.Category]).sum()
#        fig,ax = plt.subplots()
#        width = 0.35
#        rects1 = ax.bar(, men_means, width, color='r'

    
class Schwab(account):
    def __init__(self,username,password):
        super().__init__()
        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.schwab.com/public/schwab/nn/login/login.html&lang=en')
        time.sleep(2)
        browser.switch_to.frame(browser.find_element_by_id('loginIframe'))
        time.sleep(2)
        UsernameElement = browser.find_element_by_xpath("/html/body/div/div/form/div[2]/div[2]/input")
        UsernameElement.send_keys(username)
        PasswordElement = browser.find_element_by_xpath("/html/body/div/div/form/div[3]/div[2]/input")
        PasswordElement.send_keys(password)
        SubmitButton = UsernameElement = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/button")
        SubmitButton.click()
        time.sleep(10)
        actpage = browser.current_url
        joint = browser.find_element_by_id('ctl00_wpm_ac_ac_rbk_ctl00_lnkBrokerageAccountName')
        joint.click()
        time.sleep(10)
        account1 = browser.page_source
        browser.get(actpage)
        time.sleep(10)
        IRA = browser.find_element_by_id('ctl00_wpm_ac_ac_rbk_ctl01_lnkBrokerageAccountName')
        IRA.click()
        time.sleep(5)
        account2 = browser.page_source
        browser.get(actpage)
        time.sleep(10)
        Grandpa = browser.find_element_by_id('ctl00_wpm_ac_ac_rbk_ctl02_lnkBrokerageAccountName')
        Grandpa.click()
        time.sleep(10)
        account3 = browser.page_source
        browser.close()  
        
        pages = {'joint':account1,'IRA':account2,'Grandpa':account3}
        
        ticker = []    
        qty = []
        price = []
        value = []
        account = []
        
        for page in pages:
            pagebs = bs(pages[page])
            funds = pagebs.findAll(class_ = 'symbol' )
        
            for fund in funds:
                ticker.append(fund['data-symbol'])
                for i,column in enumerate(fund.parent.next_siblings):
                    #top[0] = Quantify, top[1]=Price, top[2]=Price Change, top[3]=Value
                    if i == 1:
                        qty.append(cleannum(column.get_text()))
                    if i == 3:
                        price.append(cleannum(column.get_text()))
                    if i == 7:
                        value.append(cleannum(column.get_text()))
                account.append(page)
        column_vals = [qty, price, value, account]
        self.portfolio = pd.DataFrame({'Account':'401K','Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})  
        self.add_cats()  

 
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
        page2 = browser.find_element_by_link_text('Positions')
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
    def __init__(self,username,password):
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
        account6 = pd.DataFrame({'Ticker':'Principal','Qty':1,'Price':value,'Value':value},index =[1])
        self.portfolio = account6
        self.add_cats() 


  
