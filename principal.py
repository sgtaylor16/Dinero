# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 18:20:52 2018

@author: sgtay
"""
#from dinero.dinero2 import account
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
from dinero.account import account
from dinero.dinero2 import cleannum


class Principal(account):
    def __init__(self,username,password,key):
        super().__init__()
        chrome_option = Options()
        chrome_option.add_argument(
                "user-data-dir=C:\\User\\sgtay\\AppData\\Local\\Google\\Chrome\\User Data")
        browser = webdriver.Chrome(executable_path = chromium_path,options = chrome_option)
        browser.get('https://www.principal.com')
        time.sleep(20)
        pull_down = browser.find_element_by_xpath('//*[@id="principal-primary-navbar"]/div/div[2]/ul/li[2]/a')
        pull_down.click()
        time.sleep(5)
        login = browser.find_element_by_xpath('//*[@id="principal-primary-navbar"]/div/div[2]/ul/li[2]/ul/li[3]/a')
        login.click()
        time.sleep(20)
        user = browser.find_element_by_xpath('//*[@id="userid"]')
        for character in username:
            user.send_keys(character)
            time.sleep(0.8)
        field2=browser.find_element_by_xpath('//*[@id="pass"]')
        time.sleep(5)
        for character in password:
            field2.send_keys(character)
            time.sleep(0.8)
#        field2.send_keys(password)
        time.sleep(5)
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