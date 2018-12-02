# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:07:30 2018

@author: sgtay
"""
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chromium_path = r'C:/Users/sgtay/Anaconda2/Scripts/chromedriver.exe'
profile = r'C:\Users\sgtay\AppData\Local\Google\Chrome\User Data'
from dinero.dinero2 import account
from dinero.dinero2 import cleannum
import pandas as pd

class Schwab(account):
    def __init__(self,username,password):
        super().__init__()
        
        chrome_option = Options()
        chrome_option.add_argument(
                "user-data-dir=C:\\User\\sgtay\\AppData\\Local\\Google\\Chrome\\User Data")
        browser = webdriver.Chrome(executable_path = chromium_path,options = chrome_option)
#        browser = webdriver.Chrome(executable_path = chromium_path)
        browser.get('https://www.schwab.com/public/schwab/nn/login/login.html&lang=en')
        time.sleep(15)
        browser.switch_to.frame(browser.find_element_by_id('loginIframe'))
        time.sleep(15)
        UsernameElement = browser.find_element_by_xpath("/html/body/div/div/form/div[2]/div[2]/input")
        UsernameElement.send_keys(username)
        PasswordElement = browser.find_element_by_xpath("/html/body/div/div/form/div[3]/div[2]/input")
        PasswordElement.send_keys(password)
        SubmitButton = UsernameElement = browser.find_element_by_xpath("/html/body/div/div/form/div[5]/button")
        SubmitButton.click()
        time.sleep(15)
        actpage = browser.current_url
    #    joint = browser.find_element_by_id('ctl00_wpm_ac_ac_rbk_ctl00_lnkBrokerageAccountName')
        joint = browser.find_element_by_link_text('Joint Tenant')
        joint.click()
        time.sleep(15)
        account1 = browser.page_source
        browser.get(actpage)
        time.sleep(15)
#        IRA = browser.find_element_by_id('ctl00_wpm_ac_ac_rbk_ctl01_lnkBrokerageAccountName')
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
        column_vals = [qty, price, value, account]
        self.portfolio = pd.DataFrame({'Account':'401K','Ticker':ticker,'Qty':qty,'Price':price,'Value':value,'Account':account})  
        self.add_cats()  
        
        browser.close()