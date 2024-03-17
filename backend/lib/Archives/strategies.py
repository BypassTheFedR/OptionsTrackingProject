from backend.lib.connect import connect_to_database, disconnect_from_database
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

##############################################################################
# Working on this function ChatGPT Ignore def close_strategy() for now       #
##############################################################################
# def close_strategy(strategy_ID, Active=False):
#      conn, cursor = connect_to_database()
#      cursor.execute("SELECT Open FROM Trades WHERE StrategyID = ?", (strategy_ID,))
#      trade_status = cursor.fetchall()
#      if trade_status == True:# check all trades are closed before closing strategy
#            cursor.execute("UPDATE Stategies SET ClosingPremium = ?, TotalPremium = ?, Open = ? WHERE TradeID = ?", (closing_prem, total_prem, open, trade_ID) "