# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:07:30 2018

@author: sgtay
"""
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chromium_path = r'C:/Users/sgtay/Anaconda3/Scripts/chromedriver.exe'
profile = r'C:\Users\sgtay\AppData\Local\Google\Chrome\User Data'
from dinero.dinero2 import cleannum
import pandas as pd
from dinero.account import account

from dinero.account import account

class Schwab(account):

    def webread(self,username,password):

        super().__init__()
        
        chrome_option = Options()
        chrome_option.add_argument(
                "user-data-dir=C:\\User\\sgtay\\AppData\\Local\\Google\\Chrome\\User Data")
        browser = webdriver.Chrome(executable_path = chromium_path,options = chrome_option)
        browser.get('https://www.schwab.com/public/schwab/nn/login/login.html&lang=en')
        time.sleep(10)
        browser.switch_to.frame(browser.find_element_by_id('loginIframe'))
        time.sleep(10)
        UsernameElement = browser.find_element_by_xpath('//*[@id="LoginId"]')

        UsernameElement.send_keys(username)
        time.sleep(15)
        PasswordElement = browser.find_element_by_xpath('//*[@id="Password"]')
        PasswordElement.send_keys(password)
        SubmitButton = UsernameElement = browser.find_element_by_xpath('//*[@id="LoginSubmitBtn"]')
        SubmitButton.click()
        time.sleep(15)
        actpage = browser.current_url
        joint = browser.find_element_by_link_text('Joint Tenant')
        joint.click()
        time.sleep(15)
        account1 = browser.page_source
        browser.get(actpage)
        time.sleep(25)
        IRA = browser.find_element_by_link_text('Rollover IRA')
        IRA.click()
        time.sleep(15)
        account2 = browser.page_source
        browser.get(actpage)
                
        pages = {'joint':account1,'Schwab IRA':account2}
        
        ticker = []    
        qty = []
        price = []
        value = []
        account = []
        
        for page in pages:
            pagebs = bs(pages[page])
            funds = pagebs.findAll(class_ = ['symbol','open-popup-bsb'])
        
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
        self.ledger = pd.DataFrame({'Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})  
        self.add_cats()  
        
        browser.close()

    def textread(self,path,accountname,header = 1):
        data = pd.read_csv(path,header = header)
        dropmask = data["Symbol"].apply(lambda x: ' ' not in x)
        data = data[dropmask]

        self.ledger = pd.DataFrame(columns = ['Ticker','Qty','Price','Value'])
        self.ledger['Ticker'] = data["Symbol"]
        self.ledger["Qty"] = data["Quantity"].apply(lambda x: x.replace(",","")).astype(float)
        self.ledger["Price"] = data["Price"].apply(lambda x: x.replace("$","")).astype(float)
        self.ledger["Value"] = data["Market Value"].apply(lambda x: x.replace(",","")).apply(lambda x: x.replace("$","")).astype(float)
        self.ledger["Account"] = accountname
        self.add_cats()



