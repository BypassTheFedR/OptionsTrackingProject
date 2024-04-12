from sqlalchemy import create_engine, Column, Integer, Date, String, Float, Boolean, ForeignKey, update
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
# from strategies import Strategies

# These may not be needed anymore
# from datetime import datetime, date
# import pandas as pd

# Create the SQLAlchemy engine
engine = create_engine('sqlite:///backend/data/trading.db')

# Create a session maker to interact with the database
Session = sessionmaker(bind=engine)

# Create a base class for declarative class defintion
Base = declarative_base()

class Trades(Base):
    # to construct a trade, I need to know the ID of the strategy.
    # the ID of the strategy is located within the database and is created when the strategy is created.
    # Therefore I should add the strategy to the DB first. Then add the trade which first queries the database and displays the current strategies and their ID. 
    __tablename__ = "Trades"

    TradeID = Column(Integer, primary_key=True)
    StrategyID = Column(Integer, ForeignKey('Strategies.StrategyID'))
    StrategyID = Column(Integer)
    TradeDate = Column(Date)
    OpeningPremium = Column(Float)
    ClosingPremium = Column(Float)
    TotalPremium = Column(Float)
    StrikePrice = Column(Float)
    Expiry = Column(Date)
    OptionType = Column(String)
    Open = Column(Boolean)
    Fee = Column(Float)

    # strategies = relationship("Strategies", back_populates="trades")

    default_fee = 0.06
    
    def __init__(self, strategy_ID, trade_date, opening_prem, strike_price, expiry, option_type, closing_prem=0.0, open=True,fee=default_fee):
      
        self.StrategyID = strategy_ID
        self.TradeDate = trade_date
        self.OpeningPremium = opening_prem
        self.ClosingPremium = closing_prem
        self.TotalPremium = opening_prem - closing_prem
        self.StrikePrice = strike_price
        self.Expiry = expiry
        self.OptionType = option_type
        self.Open = open
        self.Fee = fee
    
    # Function to add the first trade of a strategy
    @classmethod
    def initial_trade(cls, session, StrategyID, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType, ClosingPremium=0.0, Open=True, Fee=default_fee):
         # from strategies import Strategies
         print("Received arguments:")
         print("StrategyID:", StrategyID)
         print("TradeDate:", TradeDate)
         print("OpeningPremium:", OpeningPremium)
         print("StrikePrice:", StrikePrice)
         print("Expiry:", Expiry)
         print("OptionType:", OptionType)
         print("ClosingPremium:", ClosingPremium)
         print("Open:", Open)
         print("Fee:", Fee)


         TradeDate = datetime.strptime(TradeDate ,'%m/%d/%Y').date()
         Expiry = datetime.strptime(Expiry,'%m/%d/%Y').date()
         trade = cls(StrategyID, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType, ClosingPremium, Open, Fee)
         session.add(trade)
         session.commit()

    # Add strategy and add a trade at the same time. Not working currently.
    @classmethod
    def add_strategy_with_initial_trade(cls, Underlying, InitialInvestment, TotalContracts, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType, Active=True, ClosingPremium=0, Open=True, Fee=default_fee):
        from strategies import Strategies
        TotalPremiumReceived = OpeningPremium * TotalContracts

        # Step 1: Create a trade instance
        trade = cls(None, TradeDate, OpeningPremium, StrikePrice, Expiry, OptionType, ClosingPremium, Open, Fee)

        # Step 2: Add the trade
        trade_session = Session()
        trade_session.add(trade)
        trade_session.commit()
        trade_session.close()

        # Step 3: Create and add the strategy instance
        strategy_session = Session()
        strategy_instance = Strategies(Underlying, InitialInvestment, TotalPremiumReceived, TotalContracts, Active)
        strategy_session.add(strategy_instance)
        strategy_session.commit()

        # Step 4: Retrieve the StrategyID
        latest_strategy = strategy_session.query(Strategies).order_by(Strategies.StrategyID.desc()).first()
        strategy_id = latest_strategy.StrategyID
        strategy_session.close()

        # Step 5: Update the trade with the correct StrategyID
        trade.StrategyID = strategy_id
        trade_session.commit()
        trade_session.close()

    @classmethod    
    def display_open_strategies(cls, session):
         active_strategies = session.query(cls).filter(cls.Open == True).all()
         return active_strategies
    
session = Session()


Trades.initial_trade(session, 1, '3/22/2024', 100.0, 35, '3/28/2024', 'Call')
