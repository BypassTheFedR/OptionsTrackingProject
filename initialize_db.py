# Import necessary modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_app.database import Base

# Import your models for them to be included in Base.metadata
from sql_app.models import Strategy, Trade, Prices

# Create an instance of the engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./options_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables
Base.metadata.create_all(engine)
