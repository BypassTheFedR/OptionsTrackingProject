from connect import connect_to_database, disconnect_from_database
from datetime import datetime, date
import pandas as pd

class Strategies:
    # To calculate ROI
    def __init__(self, underlying, initial_investment, total_premium_received, total_contracts, active=True):
        self.underlying = underlying
        self.initial_investment = initial_investment
        self.total_premium_received = total_premium_received
        self.total_contracts = total_contracts
        self.total_money_risked = initial_investment
        self.calculated_average_invested = self.total_money_risked / self.total_contracts
        self.active = active  
    
    def add_strategy(self):
        conn,cursor = connect_to_database()
        cursor.execute("INSERT INTO Strategies (Underlying, InitialInvestment, TotalPremiumReceived, TotalContracts, TotalMoneyRisked, CalculatedAverageInvested, Active) VALUES (? ,? ,? ,? ,? ,? ,?)",
                        (self.underlying, self.initial_investment, self.total_premium_received, self.total_contracts, self.total_money_risked, self.calculated_average_invested, self.active))
        disconnect_from_database(conn, cursor)
        
        
class Trades:
    # to construct a trade, I need to know the ID of the strategy.
    # the ID of the strategy is located within the database and is created when the strategy is created.
    # Therefore I should add the strategy to the DB first. Then add the trade which first queries the database and displays the current strategies and their ID. 
    
    def __init__(self, strategy_ID, trade_date, opening_prem, strike_price, expiry, option_type, open=True, closing_prem=0, fee=0.06):
      
        self.strategy_ID = strategy_ID
        self.trade_date = trade_date
        self.opening_prem = opening_prem
        self.closing_prem = closing_prem
        self.total_prem = opening_prem - closing_prem
        self.strike_price = strike_price
        self.expiry = expiry
        self.option_type = option_type
        self.open = open
        self.fee = fee
    
    # Function to add the first trade of a strategy
    def initial_trade(self):
         conn, cursor = connect_to_database()
         cursor.execute("INSERT INTO Trades (StrategyID, TradeDate, OpeningPremium, ClosingPremium, TotalPremium, StrikePrice, Expiry, Type, Open, Fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (self.strategy_ID, self.trade_date, self.opening_prem, self.closing_prem, self.total_prem, self.strike_price, self.expiry, self.option_type, self.open, self.fee))
         disconnect_from_database(conn,cursor)
    
    # Function for rolling an option
    # closing_trade_premium argument 
    def roll_trade(self, trade_date, opening_premium, closing_trade_premium, ):
 
    # def close_trade(self, trade_ID, closing_prem,Open=False):
    #     conn, cursor = connect_to_database()
    #     cursor.execute("INSERT INTO Trades () ")

def display_active_strategies():
        conn, cursor = connect_to_database()
        cursor.execute("SELECT * FROM Strategies WHERE Active=True")
        active_strategies = cursor.fetchall()
        df = pd.DataFrame(active_strategies, columns=["StrategyID", "Underlying", "InitialInvestment", "TotalPremiumReceived", "TotalContracts", "TotalMoneyRisked", "CalculatedAverageInvested","Active"])
        print(df)
        disconnect_from_database(conn, cursor)

def display_closed_strategies():
        conn, cursor = connect_to_database()
        cursor.execute("SELECT * FROM Strategies WHERE Active=False")
        active_strategies = cursor.fetchall()
        df = pd.DataFrame(active_strategies, columns=["StrategyID", "Underlying", "InitialInvestment", "TotalPremiumReceived", "TotalContracts", "TotalMoneyRisked", "CalculatedAverageInvested","Active"])
        print(df)
        disconnect_from_database(conn, cursor)

def display_active_trades():
         conn, cursor = connect_to_database()
         cursor.execute("SELECT * FROM Trades WHERE Open=True")
         active_trades = cursor.fetchall()
         df = pd.DataFrame(active_trades, columns=["TradeID", "StrategyID", "Investment", "OpeningPremium", "ClosingPremium", "TotalPremium", "StrikePrice", "Expiry", "Type", "Open", "Fee"])
         print(df)
         disconnect_from_database(conn,cursor)

def display_closed_trades():
         conn, cursor = connect_to_database()
         cursor.execute("SELECT * FROM Trades WHERE Open=False")
         closed_trades = cursor.fetchall()
         df = pd.DataFrame(closed_trades, columns=["TradeID", "StrategyID", "Investment", "OpeningPremium", "ClosingPremium", "TotalPremium", "StrikePrice", "Expiry", "Type", "Open", "Fee"])
         print(df)
         # for trade in active_trades:
         #     print(trade)
         disconnect_from_database(conn,cursor)

##############################################################################
# Working on this function ChatGPT Ignore def close_strategy() for now       #
##############################################################################
def close_strategy(strategy_ID, Active=False):
      conn, cursor = connect_to_database()
      cursor.execute("SELECT Open FROM Trades WHERE StrategyID = ?", (strategy_ID,))
      trade_status = cursor.fetchall()
      if trade_status == True:# check all trades are closed before closing strategy
            cursor.execute("UPDATE Stategies SET ClosingPremium = ?, TotalPremium = ?, Open = ? WHERE TradeID = ?", (closing_prem, total_prem, open, trade_ID) "

def get_DTE(trade_ID):
     conn, cursor = connect_to_database()
     cursor.execute("SELECT Expiry FROM Trades WHERE TradeID = ?", (trade_ID,))
     result = cursor.fetchone()
     if result:
          expiry_date_str = result[0]
          expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
          today = date.today()
          dte = (expiry_date - today).days
          conn.close()
          return dte
     else:
          conn.close()
          print("No trades were found with that ID")
          return None

def close_trade(trade_ID, closing_prem,open=False):
         conn, cursor = connect_to_database()

         # Get the opening premium value
         cursor.execute("SELECT OpeningPremium FROM Trades WHERE TradeID = ?", (trade_ID,))
         result = cursor.fetchone()
         if result:
              opening_prem = result[0]
         else:
              conn.close()
              print("Trade not found.")
              return None
         
         # Calculate TotalPremium
         total_prem = opening_prem - closing_prem
         
         # Update the Trades table with the supplied and calculated data
         cursor.execute("UPDATE Trades SET ClosingPremium = ?, TotalPremium = ?, Open = ? WHERE TradeID = ?", (closing_prem, total_prem, open, trade_ID))
         conn.commit()
         conn.close()

# Mostly a development function to delete test data
def delete_trade(trade_id):
      conn, cursor = connect_to_database()
      cursor.execute("DELETE FROM Trades WHERE TradeID = ?", (trade_id,))
      conn.commit()
      conn.close()


# test_strategy = Strategies("AAPL", 3000.00, 100, 1, True)
# test_strategy.add_strategy()

display_active_strategies()

# test_trade = Trades(2, '2024-03-08', 0.80, 39.5, '2024-03-15', "Call")
# test_trade.add_trade()

display_active_trades()