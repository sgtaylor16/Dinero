# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:09:45 2018

@author: sgtay

"""

#from dinero.dinero2 import account
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
chromium_path = r'C:/Users/sgtay/Anaconda3/Scripts/chromedriver.exe'
from dinero.dinero2 import cleannum
from dinero.account import account

class Fidelity(account):
    
    def webread1(self,username,password):
        super().__init__()
        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.fidelity.com/')
        time.sleep(10)
        UsernameElement = browser.find_element_by_id("userId-input")
        for character in username:
            UsernameElement.send_keys(character)
            time.sleep(0.1)
        time.sleep(2)
        PasswordElement = browser.find_element_by_id("password")
        for character in password:
            PasswordElement.send_keys(character)
            time.sleep(0.1)
        time.sleep(2)
        SubmitButton = UsernameElement = browser.find_element_by_id('fs-login-button')
        SubmitButton.click()
        time.sleep(10)
        PositionsPage = browser.find_element_by_link_text('Account positions')
        PositionsPage.click()
        time.sleep(10)
        allaccounts = browser.find_element_by_css_selector("div.account-selector--main-wrapper")
        #Get the ROTH Account
        roth_link = allaccounts.find_element_by_link_text("ROTH IRA")
        roth_link.click()
        time.sleep(10)
        rothpage = browser.page_source
        rothbs = bs(account_page)
        browser.close()
        toptable = accountsbs.findAll(class_ = 'p-positions-tbody')[1]
        tablerows = toptable.findAll('tr')
        
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
        self.ledger = pd.DataFrame({'Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})
        self.add_cats() 

    def webread2(self,username,password):
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
        retire = browser.find_element_by_xpath('/html/body/div[4]/div[3]/div[2]/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div[4]/div[5]/div[2]/div/div[1]/span[1]')
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
        self.ledger = account5
        self.add_cats() 
        
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
