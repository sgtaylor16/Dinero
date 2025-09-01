from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import create_engine, ForeignKey, Float

class Base(DeclarativeBase):
    pass    

class InvestmentType(Base):
    __tablename__ = "investment_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("investment_types.id"), nullable=False)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)

class InvestmentPriceHistory(Base):
    __tablename__ = "investment_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    investment_id: Mapped[int] = mapped_column(ForeignKey("investments.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)


class Assets(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    investment_id: Mapped[int] = mapped_column(ForeignKey("investments.id"), nullable=False)
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False) # I will now have a history of Account assets
