from sql_app.utils.stock_utils import get_last_price
from sql_app.database import SessionLocal, engine
from datetime import datetime
from sql_app.models import Strategy, Prices

# on periodical basis retrieve stock prices for all strategies
#   Retrieve the ticker symbols for the active strategies and save them to a list. (strategies.underlying)
#   Retrieve the last quoted price for each underlying and save to dictionary with key : value of underlying : last_price
#   Update take each key value pair in the created dictionary and add them to the prices table with strategy_id, date data was accessed, last_price
#   
# print(get_last_price(["AAPL"]))

def update_prices():
    db = SessionLocal()
    
    # Retrieve the ticker symbols for the active strategies (both lists).
    active_strategies = db.query(Strategy).filter(Strategy.status=="Open").all()
    tickers = []
    strategy_ids = []

    for strategy in active_strategies:
        tickers.append(strategy.underlying)
        # print(f'Adding {strategy.underlying}')

    for strategy in active_strategies:
        strategy_ids.append(strategy.id)

    # Using list comprehension for performance reasons. This accesses the yfinace database one time instead of once per item in the list
    last_price = [get_last_price(ticker) for ticker in tickers]

    for i in range(len(strategy_ids)):
        # create the dictionary for adding to the Prices table
        price_instance = Prices(strategy_id=strategy_ids[i], data_date=datetime.now(),price=last_price[i])
        # strategy_data = {'strategy_id' : strategy_ids[i], 'data_date' : datetime.now(), 'price' : last_price[i]}
        db.add(price_instance)
    
    db.commit()
    db.close()

update_prices()