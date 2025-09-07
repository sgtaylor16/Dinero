import sqlite3
import pandas as pd
from dateutil.parser import parse


def calcPortfolioValue(datestr:str) -> pd.DataFrame:
    """
    Calculate portfolio data on a given date
    """
    date = parse(datestr)
    datestr = date.strftime("%Y-%m-%d")
    print(datestr)
    conn = sqlite3.connect('investments.db')

    #check if date is in the database
    df = pd.read_sql_query("""SELECT DISTINCT date FROM assets""", conn)
    if datestr not in df['date'].values:
        raise ValueError("Date not found in database")

    df1 = pd.read_sql_query("""SELECT accounts.name account, ticker, qty ,investment_types.name type, investments.id inv_id FROM assets
                           join accounts on assets.account_id = accounts.id
                           join investments on assets.investment_id = investments.id
                            join investment_types on investments.type_id = investment_types.id
                      where date = ?""", conn, params=(datestr,))
    
    df2 = pd.read_sql_query("""SELECT investment_id, price FROM investment_price_history
                      where date = ?""", conn, params=(datestr,))
    
    df3 = pd.merge(df1, df2, left_on='inv_id', right_on='investment_id', how='left')
    df3['value'] = df3['qty'] * df3['price']

    df3 = df3.drop(columns=['inv_id', 'investment_id'],axis=1)

    conn.close()
    return df3