import sqlite3
import pandas as pd
from dateutil.parser import parse
from models import Account,Assets,Investment,InvestmentType, InvestmentPriceHistory
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import re
from datetime import date
from dinero.dinero import target
import matplotlib.pyplot as plt

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

def plotPortfolioValue(datestr:str) -> pd.DataFrame:

    df1 = calcPortfolioValue(datestr)
    df1.drop(['bondcorrection','price','ticker','qty'],axis=1,inplace=True)

    df2 = df1.groupby(['account','type']).sum()

    accounts = df2.index.levels[0].tolist()
    types = df2.index.levels[1].tolist()

    type_x = {t: i+1 for i, t in enumerate(types)}
    colors = plt.cm.tab10.colors  # Returns tuple of RGB values
    color_map = {t: colors[i % len(colors)] for i, t in enumerate(accounts)}
    bottoms = {type: 0 for type in types}

    fig, ax = plt.subplots(figsize=(10, 6))

    for type in types:
        for account in accounts:
            height = df2.loc[(account, type), 'value'] if (account, type) in df2.index else 0
            ax.bar(type_x[type], height, bottom=bottoms[type], color=color_map[account],align='edge',width = -0.25)
            bottoms[type] += height
    ax.set_xticks(list(type_x.values()))
    ax.set_xticklabels(list(type_x.keys()))
    ax.legend(accounts, title='Accounts')

    #Now do targets
    targets = target(0.28,df1['value'].sum().sum())
    targets.rename({'IntNatl':'International','Emrg Mkts':'Emerging Markets'}, inplace=True)
    for type in types:
        if type in targets.index:
            ax.bar(type_x[type], targets[type], color='grey', width=0.25, align='edge')

    #Show the account toal value in the graph
    total_value = df1['value'].sum().sum()
    ax.text(0.05,0.95, f'Total Value: ${total_value:,.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    bytype = df1['value'].groupby(df1['type']).sum()

    compare = pd.merge(targets, bytype, left_index=True, right_index=True)
    compare['diff'] = compare['Share'] - compare['value']
    compare.loc["Total",:] = compare.sum(numeric_only=True)
    compare = compare.style.format("${:,.2f}")

    return compare

def getPortfolioDates() -> list[str]:
    """Get a list of all dates in the assets table."""
    with sqlite3.connect('investments.db') as conn:
        df = pd.read_sql_query("""SELECT DISTINCT date FROM assets""", conn)
    dates_unsorted = df['date'].tolist()
    df = pd.DataFrame(dates_unsorted, columns=['date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df['date'].tolist()

def invHistory() -> pd.DataFrame:

    #Get all dates in the assets table
    dates = getPortfolioDates()

    #For each date, calculate portfolio value
    outlist = []
    for date in dates:
         value = calcPortfolioValue(date)['value'].sum()
         outlist.append([date,value])

    return pd.DataFrame(outlist, columns=['date','value']).sort_values('date')