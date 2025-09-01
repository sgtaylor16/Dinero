from models import InvestmentType, Investment, Account
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os
import json

# Create the session
engine = create_engine("sqlite:///investments.db", echo=True)
# Create the investment types
invtypes = ['Large Cap','Small Cap','Bond','REIT','Cash','International','Unknown']
with Session(engine) as session:
    for it in invtypes:
        newtype = InvestmentType(name=it)
        session.add(newtype)
    session.commit()


for records in os.listdir('/Users/scotttaylor/Library/CloudStorage/OneDrive-Personal/Finance/Stocks'):
    if records.endswith('.json'):
        filepath = os.path.join('/Users/scotttaylor/Library/CloudStorage/OneDrive-Personal/Finance/Stocks', records)
        with open(filepath, 'r') as f:
            data_dict = json.load(f)
        for obj in data_dict:
            with Session(engine) as session:
                #Get unique values of Investment tickers
                stmt = select(Investment.ticker).distinct()
                unique_tickers = session.execute(stmt).scalars().all()
                if obj['Ticker'] not in unique_tickers:
                    inv = Investment(type_id=7, ticker=obj['Ticker'])
                    session.add(inv)
                    session.commit()


