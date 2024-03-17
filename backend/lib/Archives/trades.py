from connect import connect_to_database, disconnect_from_database
from datetime import datetime, date
import pandas as pd
  
class Trades:
    # to construct a trade, I need to know the ID of the strategy.
    # the ID of the strategy is located within the database and is created when the strategy is created.
    # Therefore I should add the strategy to the DB first. Then add the trade which first queries the database and displays the current strategies and their ID. 
    default_fee = 0.06

    def __init__(self, strategy_ID, trade_date, opening_prem, strike_price, expiry, option_type, open=True, closing_prem=0, fee=default_fee):
      
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
    # e.g. trades_instance = Trades (arguments)
    # trades_instance.initial_trade
    def initial_trade(self):
         conn, cursor = connect_to_database()
         cursor.execute("INSERT INTO Trades (StrategyID, TradeDate, OpeningPremium, ClosingPremium, TotalPremium, StrikePrice, Expiry, Type, Open, Fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (self.strategy_ID, self.trade_date, self.opening_prem, self.closing_prem, self.total_prem, self.strike_price, self.expiry, self.option_type, self.open, self.fee))
         conn.commit()
         disconnect_from_database(conn,cursor)
    
    # Function for adding trades without using a class constructor, usually will be used within the roll_trade() method
    # closing premium and total premium are set within the method
    @staticmethod
    def add_trade(strategy_ID, trade_date, opening_prem, strike_price, expiry, option_type, open=True, closing_prem=0, fee=default_fee):
         total_prem = opening_prem - closing_prem
         conn, cursor = connect_to_database()
         cursor.execute("INSERT INTO Trades (StrategyID, TradeDate, OpeningPremium, ClosingPremium, TotalPremium, StrikePrice, Expiry, Type, Open, Fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (strategy_ID, trade_date, opening_prem, closing_prem, total_prem, strike_price, expiry, option_type, open, fee))
         conn.commit()
    
    # Function for rolling an option
    # closing_trade_premium argument is for the closing trade
    # closing premium and total premium for newly opened trade will be set within the roll_trade method
    @staticmethod
    def roll_trade(trade_id, closing_trade_premium, new_trade_date, opening_premium, strike_price, expiry, open=True, closing_prem=0, fee=default_fee):
        try:
             # I need to get the old trade, update the closing premium and status
             # take values from the old trade that aren't changing strategy_ID and Type
             
             conn, cursor = connect_to_database()
             # Select the details of the old trade and import them into a call of the new trade
             try:
                cursor.execute("SELECT StrategyID, OpeningPremium, Type FROM Trades WHERE TradeID = ?", (trade_id,))
             except:
                  print("Could not retrieve data from the Trade Table")
            
             result = cursor.fetchone()
             if result:
                  strategy_id, old_trade_opening, option_type = result
                  # Verified that I was able to get values for all of these.
                  # print(strategy_id)
                  # print(old_trade_opening)
                  # print(option_type)
             else:
                  print("Trade not found.")
                  return None
                   
             # Calculate TotalPremium for the closing trade
             old_total_prem = old_trade_opening - closing_trade_premium
             old_status = False

             # Update the Trades table with the supplied and calculated data
             try:
                  cursor.execute("UPDATE Trades SET ClosingPremium = ?, TotalPremium = ?, Open = ? WHERE TradeID = ?", (closing_trade_premium, old_total_prem, old_status, trade_id))
             except Exception as e:
                  print("Could not update the old trade:", e)
             conn.commit()
                   
             total_prem = opening_premium - closing_prem
             try:
                  cursor.execute("INSERT INTO Trades (StrategyID, TradeDate, OpeningPremium, ClosingPremium, TotalPremium, StrikePrice, Expiry, Type, Open, Fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (strategy_id, new_trade_date, opening_premium, closing_prem, total_prem, strike_price, expiry, option_type, open, fee))
             except:
                  print("Could not update the new trade.")
             conn.commit()
             conn.close()
        except:
             print("Connection Failed!")
             return None

    @staticmethod
    def display_active_trades():
            conn, cursor = connect_to_database()
            cursor.execute("SELECT * FROM Trades WHERE Open=True")
            active_trades = cursor.fetchall()
            df = pd.DataFrame(active_trades, columns=["TradeID", "StrategyID", "Investment", "OpeningPremium", "ClosingPremium", "TotalPremium", "StrikePrice", "Expiry", "Type", "Open", "Fee"])
            print(df)
            disconnect_from_database(conn,cursor)

    @staticmethod
    def display_closed_trades():
            conn, cursor = connect_to_database()
            cursor.execute("SELECT * FROM Trades WHERE Open=False")
            closed_trades = cursor.fetchall()
            df = pd.DataFrame(closed_trades, columns=["TradeID", "StrategyID", "Investment", "OpeningPremium", "ClosingPremium", "TotalPremium", "StrikePrice", "Expiry", "Type", "Open", "Fee"])
            print(df)
            # for trade in active_trades:
            #     print(trade)
            disconnect_from_database(conn,cursor)

    @staticmethod
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
            print("No trades were found with that ID.")
            return None

    @staticmethod
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
    @staticmethod
    def delete_trade(trade_id):
        conn, cursor = connect_to_database()
        cursor.execute("DELETE FROM Trades WHERE TradeID = ?", (trade_id,))
        conn.commit()
        conn.close()

# test_trade = Trades(2, '2024-03-08', 0.80, 39.5, '2024-03-15', "Call")
# test_trade.initial_trade()

Trades.display_active_trades()
print("")
Trades.roll_trade(10,1.2,"2024-03-10",1.30,39.5,"2024-03-22")
Trades.display_active_trades()
Trades.display_closed_trades()