from models import InvestmentType, Investment, Account
from sqlalchemy import create_engine
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


