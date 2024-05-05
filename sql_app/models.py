from sqlalchemy import MetaData, create_engine, ForeignKey, Column, Integer, String, Float, Date, Boolean, update, func
from sqlalchemy.orm import relationship, Session, sessionmaker, declarative_base
from datetime import datetime
from sql_app.database import Base
import logging

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    underlying = Column(String)
    average_cost_basis = Column(Float)
    current_cost_basis = Column(Float)
    initial_trade_date = Column(Date)
    total_premium_received = Column(Float)
    premium_per_share = Column(Float)
    status = Column(String)
    closing_date = Column(Date)
    total_gained = Column(Float)
    
    # Define relationship to the Trades table
    trades = relationship("Trade", back_populates="strategy")
    
    # Define relationship to the Prices table
    prices = relationship("Prices", backref="strategy")
    
    def __init__(self, underlying,average_cost_basis,initial_trade_date,total_premium_received=0,times_assigned=0,status="Open",closing_date=None):
        self.underlying = underlying
        self.average_cost_basis = average_cost_basis
        self.current_cost_basis = average_cost_basis - total_premium_received
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
        initial_basis = db.query(Strategy.average_cost_basis).filter(Strategy.id == self.id).scalar()
        # print(initial_basis)

        # Calculate the new basis
        new_basis = initial_basis - total_premium_received

        # Update the current cost basis
        db.query(Strategy).filter(Strategy.id == self.id).update({Strategy.current_cost_basis: new_basis})
        
        db.commit()
    
    def update_average_cost_basis(self, db: Session):
        # This function will update the initial cost basis to be used to calculate the current cost basis
        # this lets me make decisions on what strikes are acceptable to prevent losing money

        # Initialize the variable that will be used to calculate 
        sum_trade_cost_basis = 0.0
        num_put_contracts = 0
        num_call_contracts = 0

        # Query all puts associated with strategy
        put_trades = db.query(Trade).filter(Trade.strategy_id == self.id, Trade.trade_type.ilike("put")).all()
        call_trades = db.query(Trade).filter(Trade.strategy_id == self.id, Trade.trade_type.ilike("call")).all()

        # update the sum_trade_cost_basis with put data
        for trade in put_trades:
            sum_trade_cost_basis += trade.strike * trade.num_contracts
            num_put_contracts += trade.num_contracts

        # update the sum_trade_cost_basis with call data
        for trade in call_trades:
            sum_trade_cost_basis += trade.call_purchase_price * trade.num_contracts
            num_call_contracts += trade.num_contracts
        
        average_cost_basis = sum_trade_cost_basis / (num_put_contracts + num_call_contracts)
        print(average_cost_basis)

        # Update the average cost basis
        db.query(Strategy).filter(Strategy.id == self.id).update({Strategy.average_cost_basis: average_cost_basis})

        db.commit()



    
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    strategy_id = Column(ForeignKey('strategies.id'))
    trade_type = Column(String)
    call_purchase_price = Column(Float)
    strike = Column(Float)
    expiry = Column(Date)
    opening_premium = Column(Float)
    closing_premium = Column(Float)
    num_contracts = Column(Integer)
    total_premium_received = Column(Float)
    trade_date = Column(Date)
    closing_date = Column(Date)
    assigned_price = Column(Float)
    assigned = Column(Boolean) # When updating a trade and this is true, increment times assigned in strategies
    status = Column(String)
    comments = Column(String)

    strategy = relationship("Strategy", back_populates="trades")

    def __init__(self, strategy_id, trade_type, strike, expiry, opening_premium,num_contracts,trade_date, closing_date="", call_purchase_price=0.0, closing_premium=0.0,assigned_price=None,assigned=0, status="Open", comments=None):
        self.strategy_id = strategy_id
        self.trade_type = trade_type
        self.call_purchase_price = call_purchase_price
        self.strike = strike
        self.expiry = datetime.strptime(expiry, '%m/%d/%Y')
        self.opening_premium = opening_premium
        self.closing_premium = closing_premium
        self.num_contracts = num_contracts
        self.total_premium_received = (opening_premium - closing_premium) * num_contracts
        self.trade_date = datetime.strptime(trade_date, '%m/%d/%Y')
        if closing_date:
            self.closing_date = datetime.strptime(closing_date,'%m/%d/%Y')
        else:
            self.closing_date = None
        self.assigned_price = assigned_price
        self.assigned = assigned
        self.status = status
        self.comments = comments

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
