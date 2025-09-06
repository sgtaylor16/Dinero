from models import InvestmentType, Investment, Account, Assets
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os
import json
from dateutil.parser import parse

def get_ticker_id(ticker:str) -> int:
    """Get the ID of an investment given its ticker symbol."""
    with Session(engine) as session:
        stmt = select(Investment).where(Investment.ticker == ticker)
        result = session.execute(stmt).scalar_one_or_none()
        if result:
            return result.id
        else:
            return None

# Create the session
engine = create_engine("sqlite:///investments.db", echo=True)
# Create the investment types
invtypes = ['Large Cap','Small Cap','Bond','REIT','Cash','International','Unknown','Emerging Markets']
with Session(engine) as session:
    for it in invtypes:
        newtype = InvestmentType(name=it)
        session.add(newtype)
    session.commit()

# Populate the investments table from JSON files
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

#Manually assign categories to investments
catdict = {
        "IJR": 2,
        "SCHE": 8,
        "SCHZ": 3,
        "SCHB": 1,
        "SCHD": 1,
        "SCHG" : 1,
        "SCHVB": 1,
        "SCHP": 3,
        "VCIT": 3,
        "VNQ": 4,
        "VB": 2,
        "NOTIX": 3,
        "JAVTX": 2,
        "MGIAX": 6,
        "NOSGX":2,
        "NHMAX":3,
        "VTMGX": 6,
        "VBILX": 3,
        "VTCLX": 1,
        "VETAX": 1,
        "WBIGX": 6,
        "SWVXX": 5,
        "SCHH": 4,
        "SCHF": 6,
        "SCHX": 1,
        "SCHA": 2,
        "SPTL": 3,
        "FNBGX": 3,
        "ITOT": 1,
        "TIP": 3,
        "FXAIX": 1,
        "FXNAX": 3,
        "FDRXX**":5,
        "FSPSX": 6,
        "VTI": 1,
        "PLFIX": 7,
        "JAMCX": 7,
        "VBIIX": 3,
        "FEMKX":8,
        "VBTIX":3,
        "VINIX":1,
        "SPDW":6,
        "SNVXX":3,
        "FREL":4,
        "MDYG":7,
        "FLBAX":7,
        "FLBIX":3,
        "FSIIX":6,
        "IWM":1,
        "Principal":7
    }

for ticker, category in catdict.items():
    with Session(engine) as session:
        inv = session.execute(select(Investment).where(Investment.ticker == ticker)).scalar_one_or_none()
        if inv:
            inv.type_id = category
            session.commit()

#Manually create accounts
schwabmain = Account(name="Schwab",description="Taxable Schwab Account")
schwabira = Account(name="Schwab IRA",description="Scott Schwab IRA Account")
rr401k = Account(name="RR 401K",description="RR 401K Account")
schwab_managed = Account(name="Schwab Managed",description="Schwab Managed Bond Account")
fidelity_ira = Account(name="Fidelity Roth",description="Brandy Fidelity Roth Account")
fidelity_ira2 = Account(name="Fidelity Traditional",description="Brandy Fidelity Traditional Account")
brandy401k = Account(name="IPX 401K",description="Brandy Empower Account")
brandy401kold = Account(name="IMMI 401K",description="Brandy Old 401K Account")

with Session(engine) as session:
    session.add_all([schwabmain, schwabira, rr401k, schwab_managed, fidelity_ira, fidelity_ira2, brandy401k])
    session.commit()

#Read in the history of the accounts from JSON
for records in os.listdir('/Users/scotttaylor/Library/CloudStorage/OneDrive-Personal/Finance/Stocks'):
    if records.endswith('.json'):
        filepath = os.path.join('/Users/scotttaylor/Library/CloudStorage/OneDrive-Personal/Finance/Stocks', records)
        with open(filepath, 'r') as f:
            data_dict = json.load(f)
        #parsedate
        accountdate = parse(records.split('.')[0])
        with Session(engine) as session:
            for obj in data_dict:
                    inv = session.execute(select(Investment).where(Investment.ticker == obj['Ticker'])).scalar_one_or_none()
                    if inv:
                        if 'joint' in obj['Account']:
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 1,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        elif 'rollover ira' in obj['Account'].lower():
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                        account_id= 2,
                                        qty=float(str(obj['Qty']).replace(",", "")),
                                        date=accountdate
                                    )
                                session.add(newinv)
                        elif ('ROTH IRA' in obj['Account']) or ("Roth IRA" in obj['Account']):
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 6,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        elif 'Schwab IRA' in obj['Account']:
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 2,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        elif "IPX401K" in obj['Account']:
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 7,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        elif "RR 401K" in obj['Account']:
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 3,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        elif "immi401k" in obj['Account'].lower():
                            if get_ticker_id(obj['Ticker']) is not None:
                                newinv = Assets(
                                    investment_id=get_ticker_id(obj['Ticker']),
                                    account_id= 8,
                                    qty=float(str(obj['Qty']).replace(",", "")),
                                    date=accountdate
                                )
                                session.add(newinv)
                        else:
                            raise ValueError(f"Unknown account type in record: {obj['Account']}")
                        session.commit()
