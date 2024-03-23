from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, update
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# from backend.lib.connect import connect_to_database, disconnect_from_database

# from datetime import datetime, date
# import pandas as pd

# Create the SQLAlchemy engine
engine = create_engine('sqlite:///backend/data/trading.db')

# Create a session maker to interact with the database
Session = sessionmaker(bind=engine)

# Create a base class for declarative class definition
Base = declarative_base()

class Strategies(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    underlying = Column(String)
    InitialInvestment = Column(Float)
    TotalPremiumReceived = Column(Float)
    TotalContracts  = Column(Integer)
    TotalMoneyRisked = Column(Integer)
    CalculatedAverageInvested = Column(Float)
    active = Column(Boolean)

    # Define relationship to the Trades table
    # trades = relationship("Trade", back_populates="strategy")

    # declare the class
    def __init__(self, underlying, InitialInvestment, TotalPremiumReceived, TotalContracts, active=True):
        self.underlying = underlying
        self.InitialInvestment = InitialInvestment
        self.TotalPremiumReceived = InitialInvestment
        self.TotalContracts = TotalContracts
        self.TotalMoneyRisked = InitialInvestment
        self.CalculatedAverageInvested = self.TotalMoneyRisked / self.TotalContracts
        self.active = active  
    
    @classmethod
    def add_strategy(cls, session, underlying, initial_investment, TotalPremiumReceived,TotalContracts,active=True):
        strategy = cls(underlying,initial_investment,TotalPremiumReceived,TotalContracts,active=True)
        session.add(strategy)
        session.commit()

    @classmethod    
    def display_active_strategies(cls, session):
         active_strategies = session.query(cls).filter(cls.active == True).all()
         return active_strategies
    
    @classmethod    
    def display_closed_strategies(cls, session):
         closed_strategies = session.query(cls).filter(cls.active == False).all()
         return closed_strategies
    
    @classmethod
    def close_strategy(cls, session, strategy_id):
        close_strategy = update(Strategies).where(Strategies.id == strategy_id).values(active = False)
        session.execute(close_strategy)
        session.commit()

session = Session()

# Add a new strategy
Strategies.add_strategy(session, 'AAPL', 10000.0, 500.0, 5)

# Display active strategies
active_strategies = Strategies.display_active_strategies(session)
for strategy in active_strategies:
    print(strategy.id, strategy.underlying, strategy.initial_investment)