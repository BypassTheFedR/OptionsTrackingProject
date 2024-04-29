from sqlalchemy import MetaData, create_engine, ForeignKey, Column, Integer, String, Float, Date, Boolean, update, func
from sqlalchemy.orm import relationship, Session, sessionmaker, declarative_base
from datetime import datetime
from sql_app.database import Base
import logging

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    underlying = Column(String)
    initial_cost_basis = Column(Float)
    current_cost_basis = Column(Float)
    initial_trade_date = Column(Date)
    total_premium_received = Column(Float)
    status = Column(String)
    closing_date = Column(Date)
    
    # Define relationship to the Trades table
    trades = relationship("Trade", back_populates="strategy")
    
    # Define relationship to the Prices table
    prices = relationship("Prices", backref="strategy")
    
    def __init__(self, underlying,initial_cost_basis,initial_trade_date,total_premium_received=0,times_assigned=0,status="Open",closing_date=None):
        self.underlying = underlying
        self.initial_cost_basis = initial_cost_basis
        self.current_cost_basis = initial_cost_basis - total_premium_received
        self.initial_trade_date = datetime.strptime(initial_trade_date, '%m/%d/%Y')
        self.total_premium_received = total_premium_received
        self.times_assigned = times_assigned
        self.status = status
        self.closing_date = datetime.strptime(closing_date, '%m/%d/%Y') if closing_date else None  # Parse string to date, if not None

    def update_total_premium_received(self, db: Session):
        # Calculate the total premium received
        total_premium_received = db.query(func.sum(Trade.total_premium_received)).filter(Trade.strategy_id == self.id).scalar()

        # Update the total_premium_received attribute
        db.query(Strategy).filter(Strategy.id == self.id).update({Strategy.total_premium_received: total_premium_received})

        # Get the initial cost basis
        initial_basis = db.query(Strategy.initial_cost_basis).filter(Strategy.id == self.id).scalar()
        print(initial_basis)

        # Calculate the new basis
        new_basis = initial_basis - total_premium_received

        # Update the current cost basis
        db.query(Strategy).filter(Strategy.id == self.id).update({Strategy.current_cost_basis: new_basis})
        
        db.commit()

    
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    strategy_id = Column(ForeignKey('strategies.id'))
    trade_type = Column(String)
    strike = Column(Float)
    expiry = Column(Date)
    opening_premium = Column(Float)
    closing_premium = Column(Float)
    num_contracts = Column(Integer)
    total_premium_received = Column(Float)
    trade_date = Column(Date)
    assigned_price = Column(Float)
    assigned = Column(Boolean) # When updating a trade and this is true, increment times assigned in strategies

    strategy = relationship("Strategy", back_populates="trades")

    def __init__(self, strategy_id, trade_type, strike, expiry, opening_premium,num_contracts,trade_date,closing_premium=0.0,assigned_price=None,assigned=0):
        self.strategy_id = strategy_id
        self.trade_type = trade_type
        self.strike = strike
        self.expiry = datetime.strptime(expiry, '%m/%d/%Y')
        self.opening_premium = opening_premium
        self.closing_premim = closing_premium
        self.num_contracts = num_contracts
        self.total_premium_received = (opening_premium - closing_premium) * num_contracts
        self.trade_date = datetime.strptime(trade_date, '%m/%d/%Y')
        self.assigned_price = assigned_price
        self.assigned = assigned

class Prices(Base):

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    strategy_id = Column(ForeignKey('strategies.id'))
    data_date = Column(Date)
    price = Column(Float)

    def __init__(self, strategy_id, data_date, price):
        self.strategy_id = strategy_id
        self.data_date = data_date
        self.price = price
