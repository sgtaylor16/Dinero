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

    df = pd.read_sql_query("""SELECT name,account_id, ticker, qty FROM assets
                           join accounts on assets.account_id = accounts.id
                           join investments on assets.investment_id = investments.id
                      where date = ?""", conn, params=(datestr,))
    conn.close()
    return df