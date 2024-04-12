import os
import sqlite3

# Future funcionality ideas:
# To allow multiple users, New Table with users, Strategy Table would need a UserID Foreign Key "FOREIGN KEY (UserID) REFERENCES Users(UserID)"

def create_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # (Future Use) Create Users Table
    # cursor.execute('''CREATE TABLE USERS (
    #                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    #                Username TEXT,
    #                 )''')
    
    # Create Strategies Table
    cursor.execute('''CREATE TABLE Strategies (
                   StrategyID INTEGER PRIMARY KEY AUTOINCREMENT,
                   Underlying TEXT,
                   InitialInvestment REAL,
                   TotalPremiumReceived REAL,
                   TotalContracts INTEGER,
                   TotalMoneyRisked REAL,
                   CalculatedAverageInvested REAL,
                   Active BOOLEAN
                    )''')
    
    # Create Trades Table
    cursor.execute('''CREATE TABLE Trades (
                   TradeID INTEGER PRIMARY KEY AUTOINCREMENT,
                   StrategyID INTEGER,
                   TradeDate DATE,
                   OpeningPremium REAL,
                   ClosingPremium REAL,
                   TotalPremium REAL,
                   StrikePrice REAL,
                   Expiry DATE,
                   OptionType TEXT,
                   Open BOOLEAN,
                   Fee REAL,
                   FOREIGN KEY (StrategyID) REFERENCES Strategies(StrategyID)   
                   )''')

current_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(current_directory, '..', 'data')
database_path = os.path.join(data_directory, 'trading.db')
create_db(database_path)
