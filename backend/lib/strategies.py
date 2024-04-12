from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, update
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from trades import Trades


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
    Underlying = Column(String)
    InitialInvestment = Column(Float)
    TotalPremiumReceived = Column(Float)
    TotalContracts  = Column(Integer)
    TotalMoneyRisked = Column(Integer)
    CalculatedAverageInvested = Column(Float)
    Active = Column(Boolean)

    # Define relationship to the Trades table
    # trades = relationship("Trades", back_populates="strategies")

    # Define the default fee
    default_fee = 0.06

    # declare the class
    def __init__(self, underlying, InitialInvestment,TotalPremiumReceived, TotalContracts, active=True):
        self.Underlying = underlying
        self.InitialInvestment = InitialInvestment
        self.TotalPremiumReceived = TotalPremiumReceived
        self.TotalContracts = TotalContracts
        self.TotalMoneyRisked = InitialInvestment
        self.CalculatedAverageInvested = self.TotalMoneyRisked / self.TotalContracts
        self.Active = active  
    
    @classmethod
    def add_strategy(cls, session, Underlying, InitialInvestment, TotalPremiumReceived,TotalContracts,Active=True):
        strategy = cls(Underlying,InitialInvestment,TotalPremiumReceived,TotalContracts,Active)
        session.add(strategy)
        session.commit()
        latest_strategy_id = session.query(cls).order_by(cls.StrategyID.desc()).first()
        return latest_strategy_id

    # Add strategy and add a trade at the same time. Not working currently.
    @classmethod
    def add_strategy_with_initial_trade(cls, Underlying, InitialInvestment, TotalContracts, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType, Active=True, ClosingPremium=0, Open=True, Fee=default_fee):
        from trades import Trades
        TotalPremiumReceived = OpeningPremium * TotalContracts

        # Step 1: Strategy Session:
        strategy_session = Session()
        strategy = cls(Underlying, InitialInvestment, TotalPremiumReceived, TotalContracts, Active)
        strategy_session.add(strategy)
        strategy_session.commit()

        # Step 2: Retrieve the StrategyID:
        latest_strategy = strategy_session.query(cls).order_by(cls.StrategyID.desc()).first()
        strategy_id = latest_strategy.StrategyID
        print(strategy_id)

        # Step 3: Close the Strategy session
        strategy_session.close()

        # Step 4: Create a trade class session
        trade_session = Session()

        # Add trade using the recently created strategy_id
        Trades.initial_trade(trade_session, strategy_id, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType)
        trade_session.commit()
        trade_session.close()

    @classmethod    
    def display_active_strategies(cls, session):
         active_strategies = session.query(cls).filter(cls.Active == True).all()
         return active_strategies
    
    @classmethod    
    def display_closed_strategies(cls, session):
         closed_strategies = session.query(cls).filter(cls.Active == False).all()
         return closed_strategies
    
    @classmethod
    def close_strategy(cls, session, strategy_id):
        close_strategy = update(Strategies).where(Strategies.StrategyID == strategy_id).values(Active = False)
        session.execute(close_strategy)
        session.commit()

    # Need a method to update the strategy, might be part of the trades class

session = Session()

# Add a strategy without relatinships established
Strategies.add_strategy(session, 'RBLX', 10000.0, 100.0, 5)

# Add a new strategy
# latest_id = Strategies.add_strategy(session, '528', 10000.0, 500.0, 5)
# Trades.initial_trade(session, latest_id, '3/22/2024', 100.0, 200.0, '3/28/2024', 'Call')

# Add a strategy with a trade
# Strategies.add_strategy_with_initial_trade('AAPL', 9999.0, 5, '3/22/2024', 100, 200, '3/28/2024', "Call")


# Display active strategies
active_strategies = Strategies.display_active_strategies(session)
for strategy in active_strategies:
    print(strategy.StrategyID, strategy.Underlying, strategy.InitialInvestment)