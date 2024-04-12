from sqlalchemy import MetaData, create_engine, ForeignKey, Column, Integer, String, Float, Date, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime



class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True)
    underlying = Column(String)
    initial_cost_basis = Column(Float)
    current_cost_basis = Column(Float)
    initial_trade_date = Column(Date)
    total_premium_received = Column(Float)
    status = Column(String)
    closing_date = Column(Date)
    
    # trades = relationship("Trade", backref="strategies")
    
    def __init__(self, underlying,initial_cost_basis,initial_trade_date,total_premium_received,times_assigned=0,status="Open",closing_date=None):
        self.underlying = underlying
        self.initial_cost_basis = initial_cost_basis
        self.current_cost_basis = initial_cost_basis - total_premium_received
        self.initial_trade_date = datetime.strptime(initial_trade_date, '%m/%d/%Y')
        self.total_premium_received = total_premium_received
        self.times_assigned = times_assigned
        self.status = status
        self.closing_date = datetime.strptime(closing_date, '%m/%d/%Y') if closing_date else None  # Parse string to date, if not None
    
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    strategy_id = Column(ForeignKey('strategies.id'))
    trade_type = Column(String)
    strike = Column(Float)
    expiry = Column(Date)
    premium_per_contract = Column(Float)
    num_contracts = Column(Integer)
    total_premium_received = Column(Float)
    trade_date = Column(Date)
    assigned_price = Column(Float)
    assigned = Column(Boolean) # When updating a trade and this is true, increment times assigned in strategies
    # strategies = relationship("Strategy", backref="trades")

    def __init__(self, strategy_id, strike, expiry, premium_per_contract,num_contracts,trade_date,assigned_price=None,assigned=0):
        self.strategy_id = strategy_id
        self.strike = strike
        self.expiry = datetime.strptime(expiry, '%m/%d/%Y')
        self.premium_per_contract = premium_per_contract
        self.num_contracts = num_contracts
        self.total_premium_received = premium_per_contract * num_contracts
        self.trade_date = datetime.strptime(trade_date, '%m/%d/%Y')
        self.assigned_price = assigned_price
        self.assigned = assigned

# Base.metadata.create_all(engine)
session = Session()
strategy1 = Strategy("AAPL",170.0,'3/22/2024',1)
trade1 = Trade(2,170.0,'3/28/2024',1,1,'3/22/2024')
session.add(strategy1)
session.add(trade1)
session.commit()
session.close()
