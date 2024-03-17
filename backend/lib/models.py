from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Float, Date, Boolean
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Create the SQLAlchemy engine
engine = create_engine('sqlite:///backend/data/trading.db')

# Create a base class for declarative class definitions
Base = declarative_base()

class Strategy(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    underlying = Column(String)
    initial_investment = Column(Float)
    total_premium_received = Column(Float)
    total_contracts = Column(Integer)
    total_money_risked = Column(Integer)
    calculated_average_invested = Column(Float)
    active = Column(Boolean)

    # Define relationship to the Trades table
    trades = relationship("Trade", back_populates="strategy")

# Define the Trade Model
class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'))
    trade_date = Column(Date)
    opening_prem = Column(Float)
    closing_prem = Column(Float)
    total_prem = Column(Float)
    strike_price = Column(Float)
    expiry = Column(Date)
    option_type = Column(String)
    open = Column(Boolean)
    fee = Column(Float)

    # Define the relationship between Strategy and Trade
    trades = relationship("Trade", back_populates="strategy")

# Create the database tables
Base.metadata.create_all(engine)

# Create a sessionmaker to interact with the database
Session = sessionmaker(bind=engine)
