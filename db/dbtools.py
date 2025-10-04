import sqlite3
import pandas as pd
from dateutil.parser import parse
from models import Account,Assets,Investment,InvestmentType, InvestmentPriceHistory
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import re
from datetime import date

def checkifbondticker(ticker:str) -> bool:
    # Check if string has both numbers AND letters
    pattern = r'^(?=.*[A-Za-z])(?=.*\d).*$'
    return bool(re.match(pattern, ticker))

def calcPortfolioValue(datestr:str) -> pd.DataFrame:
    """
    Calculate portfolio data on a given date
    """
    date = parse(datestr)
    datestr = date.strftime("%Y-%m-%d")
    conn = sqlite3.connect('investments.db')

    #check if date is in the database
    df = pd.read_sql_query("""SELECT DISTINCT date FROM assets""", conn)
    if datestr not in df['date'].values:
        raise ValueError("Date not found in database")

    df1 = pd.read_sql_query("""SELECT accounts.name account, ticker, qty ,investment_types.name type, investments.id inv_id,bondcorrection FROM assets
                           join accounts on assets.account_id = accounts.id
                           join investments on assets.investment_id = investments.id
                            join investment_types on investments.type_id = investment_types.id
                            join rules on accounts.id = rules.account_id
                      where date = ?""", conn, params=(datestr,))
    
    df2 = pd.read_sql_query("""SELECT investment_id, price FROM investment_price_history
                      where date = ?""", conn, params=(datestr,))
    
    df3 = pd.merge(df1, df2, left_on='inv_id', right_on='investment_id', how='left')
    df3['value'] = df3['qty'] * df3['price']
    # Adjust bond values if ticker looks like a bond
    for index,row in df3.iterrows():
        if row['bondcorrection'] and checkifbondticker(row['ticker']):
            df3.at[index,'value'] = (row['qty'] / 100) * row['price']

    df3 = df3.drop(columns=['inv_id', 'investment_id'],axis=1)

    conn.close()
    return df3

def getTickerID(ticker:str,session:Session) -> int:
    """Get the ID of an investment given its ticker symbol."""
    stmt = select(Investment).where(Investment.ticker == ticker)
    result = session.execute(stmt).scalar_one_or_none()
    if result:
        return result.id
    else:
        return None
        
def addTicker(ticker:str, session:Session, type_id:int=7) -> None:
    """Add a new ticker to the investments table."""
    #Check if ticker already exists
    stmt = select(Investment).where(Investment.ticker == ticker)
    result = session.execute(stmt).scalar_one_or_none()
    if result:
        print(f"Ticker {ticker} already exists in database.")
        return
    inv = Investment(type_id=type_id, ticker=ticker)
    session.add(inv)
    session.flush()  # Flush instead of commit to make the ticker available for queries
    return

def readStatement(df:pd.DataFrame):
    """Read statments from a dataframe and populate the database."""
    #Make sure df has columns Ticker, Qty, Price, Account, Date
    if not all(col in df.columns for col in ['Ticker', 'Qty', 'Price', 'Account', 'Date']):
        raise ValueError("DataFrame must have columns Ticker, Qty, Price, Account, Date")
    
    engine = create_engine("sqlite:///investments.db", echo=True)
    with Session(engine) as session:
        accountname = df['Account'].iloc[0]
        #Check if account exists
        stmt = select(Account).where(Account.name == accountname)
        result = session.execute(stmt).scalar_one_or_none()
        if result:
            account_id = result.id
        else:
            raise ValueError(f"Account {accountname} not found in database")
        #Get the date of the statement
        statementdate = parse(df['Date'].iloc[0]).date()

        for index, row in df.iterrows():
            ticker = row['Ticker']
            qty = row['Qty']
            price = row['Price']
            #Find the ticker ID, if it doesn't exist, add it
            ticker_id = getTickerID(ticker, session)
            if ticker_id is None:
                if checkifbondticker(ticker):
                    addTicker(ticker, session, type_id=3)
                else:
                    addTicker(ticker, session)
                ticker_id = getTickerID(ticker, session)
            #Add to assets table
            asset = Assets(account_id=account_id, investment_id=ticker_id, date=statementdate, qty=qty)
            session.add(asset)

            #Add to investment price history table if it doesn't exist
            if ifTickerDateExists(ticker,statementdate,session):
                continue
            else:
                pricehistory = InvestmentPriceHistory(investment_id=ticker_id, date=statementdate, price=price)
                session.add(pricehistory)
        session.commit()

def ifTickerDateExists(ticker:str,datecheck:date,session:Session) -> bool:
    """Check if an investment price history record exists for a given ticker and date."""
    ticker_id = getTickerID(ticker, session)
    if ticker_id is None:
        return False
    stmt = select(InvestmentPriceHistory).where(InvestmentPriceHistory.investment_id == ticker_id).where(InvestmentPriceHistory.date == datecheck)
    result = session.execute(stmt).scalar_one_or_none()
    if result is None:
        return False
    else:
        return True
    
def addAccountAsset(accountname:str,ticker:str,qty:float,date:str,value:float,session:Session| None=None) -> None:
    """Add an account and asset if they don't exist."""
    if session is None:
        engine = create_engine("sqlite:///investments.db", echo=True)
        session = Session(engine)

    #Check if account exists
    stmt = select(Account).where(Account.name == accountname)
    result = session.execute(stmt).scalar_one_or_none()
    if result:
        account_id = result.id
    else:
        raise ValueError(f"Account {accountname} not found in database")

    #Check if ticker exists
    ticker_id = getTickerID(ticker, session)
    if ticker_id is None:
        raise ValueError(f"Ticker {ticker} not found in database")

    #Add to assets table
    asset_date = parse(date).date()
    asset = Assets(account_id=account_id, investment_id=ticker_id, date=asset_date, qty=qty)
    session.add(asset)

    #Add to investment price history table if it doesn't exist
    if ifTickerDateExists(ticker,asset_date,session):
        return
    else:
        pricehistory = InvestmentPriceHistory(investment_id=ticker_id, date=asset_date, price=value/qty)
        session.add(pricehistory)
    session.commit()

    if session is None:
        session.close()
        
    return
