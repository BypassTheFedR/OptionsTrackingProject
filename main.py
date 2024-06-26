#############################################################################
## Option tracking software made by Chaotic Neutral                        ##
## Start the app on localhost by running from the main directory           ##
##    uvicorn sql_app.main:app --reload                                    ##
## Serve the app to the local network by running:                          ## 
##    uvicorn main:app --reload -- host 0.0.0.0 --port 8000                ##
## Documentation inprogress                                                ##
############################################################################# 

import logging
import schedule
import time
import signal
import sys
from threading import Thread
from datetime import datetime
from pytz import timezone
from typing import Optional

from fastapi import FastAPI, Request, Header, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
import jinja2.exceptions

from sql_app.database import SessionLocal, engine
from sql_app import models
from sql_app import historical

models.Base.metadata.create_all(bind=engine)

# * scheduler_running = True

# Functions and schedulers to update prices daily.
def update_prices_daily():
    # get the current time in PST
    pst = timezone('US/Pacific')
    current_time = datetime.now(pst)

    # Check if it's 1:30 PM PST
    if current_time.hour == 13 and current_time.minute == 30:
        # call the update_prices function from historical library
        historical.update_prices()
        print("Prices upated at 1:30 PM PST")

def stop_scheduler():
    global scheduler_running
    scheduler_running = False

def signal_handler(sig, frame):
    print("Stopping scheduler...")
    stop_scheduler()

def run_scheduler():
    # Schedule the update_prices_daily function to run daily at 1:30 PM PST
    schedule.every().day.at('13:30').do(update_prices_daily)
    # * global scheduler_running

    # Run the schedule in a separate thread
    while True:
    # *while scheduler_running:
        schedule.run_pending()
        time.sleep(60)

# Set up signal handler
#  * signal.signal(signal.SIGINT, signal_handler)

# Start the schedule in a separate thread
scheduler_thread = Thread(target=run_scheduler)
scheduler_thread.start()

# configure logging
logging.basicConfig(level=logging.INFO)

# Define a logger
logger = logging.getLogger(__name__)

# Get the current date for use in default values on the page
current_date = datetime.now().strftime("%Y-%m-%d")

app = FastAPI()

# Mapped to the templates folder in my apps directory
templates = Jinja2Templates(directory="sql_app/templates")

# Mount th static files directory
app.mount("/static", StaticFiles(directory="sql_app/styles"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/', response_class=HTMLResponse)
async def home_page(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        strategies = db.query(models.Strategy).filter(models.Strategy.status == "Open").all()
        prices = db.query(models.Prices).all()
        
        context = {'request': request, 'strategies': strategies, 'prices': prices}

        
        for strategy in strategies:
            # Gets a trade object based on strategy id
            trade = db.query(models.Trade).filter(models.Trade.strategy_id == strategy.id).order_by(desc(models.Trade.id)).first()            
            
            if trade == None:
                print("Add the first trade for this strategy")
                # Sets trategy_type_str to "No trades" if a trade has not yet been assigned
                strategy_type_str = "No trades"
                strategy.total_gained = None
            else:
                strategy_type_str = trade.trade_type
            
            last_price_query = db.query(models.Prices).filter(models.Prices.strategy_id == strategy.id).order_by(desc(models.Prices.id)).first()
            last_price = last_price_query.price if last_price_query else 0.0

            # strategy.total_gained = strategy.total_premium_received - strategy.average_cost_basis + last_price
            if strategy_type_str.lower() == "call":
                strategy.total_gained = strategy.total_premium_received - strategy.average_cost_basis + last_price
            elif strategy_type_str.lower() == "put":
                strategy.total_gained = strategy.total_premium_received
            else:
                strategy.total_gained = 0.0
            
            # Future functionality to calculate total_gained and ROI taking into account open short positions
            # yfinance.Ticker.option_chain(Date) returns a pandas like dataframe with option information
            # E.G. Total_gained = Total_premium_received - average_cost_basis + last_price - short_position

        
        if hx_request:
            return templates.TemplateResponse("table_main.html", context)
        return templates.TemplateResponse("main.html", context)
    
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"An error occurred: {e}")
        
        # Render an error message directly without redirecting
        error_message = "An error occurred. Please try again later."
        print(error_message)
        return HTMLResponse(content=f"<h1>{error_message}</h1>", status_code=500)

@app.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request" :  request})

# @app.get("/main/")

@app.get("/add_strategy/")
async def add_strategy_form(request: Request):
    return templates.TemplateResponse("add_strategy.html", {"request" : request})

@app.post("/add_strategy/")
async def add_strategy(
    request: Request,
    underlying: str = Form(...),
    average_cost_basis: float = Form(...),
    initial_trade_date: str = Form(...),
    db: Session = Depends(get_db)
):    
    # Parse (Convert?) the date string 
    parsed_date = datetime.strptime(initial_trade_date,'%Y-%m-%d')

    # Format the date string as desired
    formatted_date = parsed_date.strftime('%m/%d/%Y')
    
    # Create a Strategy object
    new_strategy = models.Strategy(
        underlying=underlying,
        average_cost_basis=average_cost_basis,
        initial_trade_date=formatted_date
    )
    
    # Add the new Strategy object to the session
    db.add(new_strategy)
    
    # Commit the transaction
    db.commit()
    db.refresh(new_strategy)

    # Update the prices after adding a strategy
    historical.update_prices()
    
    # Redirect the user to the root menu using GET method
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

class add_strategy(BaseModel):
    underlying: str 
    average_cost_basis: float
    initial_trade_date: str

@app.get('/update_prices')
async def update_prices():
    # Updates the price of current strategies
    historical.update_prices()

    # Return to root menu
    return RedirectResponse(url="/")

@app.post("/close_strategy")
async def close_strategy(strategyId: str = Form(...), db: Session = Depends(get_db)):
    # Retrieve the strategy from the database
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategyId).first()

    # Update the strategy status
    strategy.status = "Closed"
    db.commit()

    # Return a success response
    return {"Message": "Strategy closed succesfully"}

@app.get("/add_trade/")
async def add_trade_form(request: Request, strategy_id: int, db: Session = Depends(get_db)):
    # Retrive the strategy from the databaes based on the strateg_id
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()

    trade = db.query(models.Trade).filter(models.Trade.strategy_id == strategy_id).order_by(desc(models.Trade.id)).first()

    purchase_price = "{:.2f}".format(trade.call_purchase_price) if trade else 0.0
    
    if strategy is None:
        # Handle the case where the strategy is nto found
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return templates.TemplateResponse("add_trade.html", {"request" : request, "strategy_id": strategy_id, "strategy" : strategy, "current_date" : current_date, "purchase_price" : purchase_price})

# Function for adding trades to the Trades class
@app.post("/add_trade/")
async def add_trade(
    request: Request,
    strategy_id: int = Form(...),
    trade_type: str = Form(...),
    call_purchase_price: float = Form(...),
    strike: float = Form(...),
    expiry: str = Form(...),
    opening_premium: float = Form(...),
    num_contracts: int = Form(...),
    trade_date: str = Form(...),
    db: Session = Depends(get_db)
):
    # Parse the date string because the format from the html is %Y-%m-%d
    # therefore the data needs to be converted to a string, reformatted
    # and then set as a datetime data type
    parsed_expiry = datetime.strptime(expiry,'%Y-%m-%d')
    parsed_trade_date = datetime.strptime(trade_date,'%Y-%m-%d')

    # Format the date string as desired
    formatted_expiry = parsed_expiry.strftime('%m/%d/%Y')
    formatted_trade_date = parsed_trade_date.strftime('%m/%d/%Y')

    # Create a trade object
    new_trade = models.Trade(
        strategy_id=strategy_id,  # Ensure that strategy_id is included
        trade_type=trade_type,
        call_purchase_price=call_purchase_price,
        strike=strike,
        expiry=formatted_expiry,
        opening_premium=opening_premium,
        num_contracts=num_contracts,
        trade_date=formatted_trade_date 
    )
    # Need to fix: This is a work around for the case of a put where the form requires a value for purchase_price
    # 0.0 is passed by default and we update it to back to None here
    # if new_trade.trade_type.lower() == "put":
    #     new_trade.call_purchase_price = None

    # Add the new trade to the session
    db.add(new_trade)

    # Commit the transaction
    db.commit()

    # Recalculates trade  data metrics and updates accordingly

    # Retrive the strategy by the strategy_id
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()

    # Update the total_premium_received attribute of the strategy
    strategy.update_total_premium_received(db)

    # Update the average_cost_basis
    strategy.update_average_cost_basis(db)
    
    # Redirect the user to the root menu using GET method
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/close_trade/")
async def close_trade_form(request: Request, strategy_id: int, db: Session = Depends(get_db)):
    # Retrive the strategy from the databaes based on the strategy_id
    # Retrive the trade, add a closing premium, set assigned to False/ True (False by default), and add an assigned price
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    trades = db.query(models.Trade).filter(models.Trade.strategy_id == strategy_id).filter(models.Trade.status == "Open")

    # current_date = datetime.now().strftime("%Y-%m-%d")

    if strategy is None:
        # Handle the case where the strategy is not found
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if trades is None:
        # Handle the case where the trade is not found
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return templates.TemplateResponse("close_trade.html", {"request" : request, "strategy_id": strategy_id, "strategy" : strategy, "trades" : trades, "current_date" : current_date})

# Function for adding trades to the Trades class
@app.post("/close_trade/")
async def close_trade(
    # request: Request,
    strategy_id: int = Form(...),
    trade_id: int = Form(...),
    trade_type: str = Form(...),
    closing_strike: float = Form(...),
    old_opening_premium: float = Form(...),
    old_expiry: str = Form(...),
    num_contracts: int = Form(...),
    closing_premium: float = Form(...),
    closing_date: str = Form(...),
    contracts_closed: int = Form(...),
    assigned: str = Form(...),
    assigned_price: float = Form(...),
    old_trade_date: str = Form(...),
    db: Session = Depends(get_db)
):
    # Parse the date string, resulting type is datetime
    parsed_expiry = datetime.strptime(old_expiry,'%Y-%m-%d')
    parsed_closing_date = datetime.strptime(closing_date,'%Y-%m-%d')
    parsed_trade_date = datetime.strptime(old_trade_date,'%Y-%m-%d')

    # Format the date string as desired, resulting type is string
    formatted_expiry = parsed_expiry.strftime('%m/%d/%Y')
    formatted_closed_date = parsed_closing_date.strftime('%m/%d/%Y')
    formatted_trade_date = parsed_trade_date.strftime('%m/%d/%Y')

    # Check if all trades were closed, if not handle appropriately, if so close the trade
    # Future: add specific code for handling assignments
    if contracts_closed == num_contracts:
        # retrieve the trade by trade id
        closing_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

        #  Set values using the closing_trade object
        closing_trade.closing_premium = closing_premium
        closing_trade.total_premium_received = (old_opening_premium - closing_premium) * num_contracts
        closing_trade.status = "Closed"
        closing_trade.closing_date = parsed_closing_date
    
    else:
        # Create a trade object
        new_trade = models.Trade(
            strategy_id=strategy_id,  # Ensure that strategy_id is included
            trade_type=trade_type,
            strike=closing_strike,
            expiry=formatted_expiry,
            opening_premium=old_opening_premium,
            num_contracts=num_contracts - contracts_closed,
            trade_date=formatted_trade_date     
        )
       
        # Add the new trade to the session
        db.add(new_trade)

        # Close trades that are not remaining open
        closing_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

        # Do data operations
        closing_trade.closing_premium = closing_premium
        closing_trade.num_contracts = contracts_closed
        closing_trade.total_premium_received = (old_opening_premium - closing_premium) * closing_trade.num_contracts
        closing_trade.status = "Closed"

    # Commit the transaction
    db.commit()

    # Retrive the strategy by the strategy_id
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()

    # Update the total_premium_received, average_cost_basis, and new_cost_basis attribute of the strategy
    strategy.update_total_premium_received(db)
    strategy.update_average_cost_basis(db)
    strategy.update_new_cost_basis(db)
    
    # Redirect the user to the root menu using GET method
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# In rolling a trade we need to close the data for the old trade.
# Closing the old trade involves the following:
# Update the closing_premium for the trade, 
# recalculate the total_premium_received
# Add the new trade
# Update the total_premium_received in the strategies table
#   - Sum the total_premium_received in the trades table for that strategy id
#

# Roll trade form get request
# Data needed:
# closing_premium for old trade
# closing_date for old trade (Default today)
# number of contracts closed (Default number open for that trade_id)
# opening_premium for new trade
# opening date for new trade (Default today)
# Number of new contracts opened (Default number open for that trade_id)
@app.get("/roll_trade/")
async def roll_trade_form(request: Request, strategy_id: int, db: Session = Depends(get_db)):
    # Retrive the strategy from the databaes based on the strategy_id
    # Retrive the trade, add a closing premium, set assigned to False/ True (False by default), and add an assigned price
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    trades = db.query(models.Trade).filter(models.Trade.strategy_id == strategy_id).filter(models.Trade.status == "Open")

    # current_date = datetime.now().strftime("%Y-%m-%d")

    if strategy is None:
        # Handle the case where the strategy is not found
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if trades is None:
        # Handle the case where the trade is not found
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return templates.TemplateResponse("roll_trade.html", {"request" : request, "strategy_id": strategy_id, "strategy" : strategy, "trades" : trades, "current_date" : current_date})

@app.post("/roll_trade/")
async def roll_trade(
    strategy_id: int = Form(...),
    old_trade_id: int = Form(...),
    trade_type: str = Form(...),
    old_opening_premium: float = Form(...),
    closing_strike: float = Form(...),
    old_expiry: str = Form(...),
    old_num_contracts: int = Form(...),
    call_purchase_price: Optional[float] = Form(None),  # Make this field optional with a default value of None
    closing_premium: float = Form(...),
    closing_date: str = Form(...),
    rolled_contracts: int = Form(...),
    opening_premium: float = Form(...),
    new_strike: float = Form(...),
    new_expiry: str = Form(...),
    opening_date: str = Form(...),
    db: Session = Depends(get_db)
):
    # Parse the date string 
    parsed_old_expiry = datetime.strptime(old_expiry,'%Y-%m-%d')
    parsed_closing_date = datetime.strptime(closing_date,'%Y-%m-%d')
    parsed_opening_date = datetime.strptime(opening_date,'%Y-%m-%d')
    parsed_new_expiry = datetime.strptime(new_expiry,'%Y-%m-%d')

    # Format the date string as desired
    formatted_old_expiry = parsed_old_expiry.strftime('%m/%d/%Y')
    formatted_closing_date = parsed_closing_date.strftime('%m/%d/%Y')
    formatted_opening_date = parsed_opening_date.strftime('%m/%d/%Y')
    formatted_new_expiry = parsed_new_expiry.strftime('%m/%d/%Y')

    # Check if all trades were closed, if not handle appropriately
    if rolled_contracts == old_num_contracts:
        # Update the closing trade using an update query
        db.query(models.Trade).filter(models.Trade.id == old_trade_id).update(
            {
                models.Trade.closing_premium: closing_premium,
                models.Trade.closing_date: parsed_closing_date,
                models.Trade.total_premium_received: (old_opening_premium - closing_premium) * old_num_contracts,
                models.Trade.status: "Closed"
            }
        )

        new_trade = models.Trade(
            strategy_id=strategy_id,  # Ensure that strategy_id is included
            trade_type=trade_type,
            strike=new_strike,
            expiry=formatted_new_expiry,
            opening_premium=opening_premium,
            num_contracts=old_num_contracts,
            trade_date=formatted_opening_date     
        )
        print("Is the problem here? - 4")      
        # Add the new trade to the session
        db.add(new_trade)
    
    else:
        # If not all trades are rolled we need to close the trades that were closed,
        # create a corresponding new trade with the trades that remain open,
        # and create a new trade with the trades that were rolled.
        # Future versions: While this is a rare occurence, 
        updated_old_trade = models.Trade( # Misnomer, it's not actually updating, but creating a new trade record, this is fine for now
            strategy_id=strategy_id,  # Ensure that strategy_id is included
            trade_type=trade_type,
            call_purchase_price=call_purchase_price,
            strike=closing_strike,
            expiry=formatted_old_expiry,
            opening_premium=old_opening_premium,
            num_contracts=old_num_contracts - rolled_contracts,
            trade_date=formatted_closing_date     
        )

        new_trade = models.Trade(
            strategy_id=strategy_id,  # Ensure that strategy_id is included
            trade_type=trade_type,
            call_purchase_price=call_purchase_price,
            strike=new_strike,
            expiry=formatted_new_expiry,
            opening_premium=opening_premium,
            num_contracts=rolled_contracts,
            trade_date=formatted_opening_date     
        )
       
        # Add the new trade to the session
        db.add(updated_old_trade)
        # Add the new trade to the session
        db.add(new_trade)

        # Close trades that are not remaining open
        closing_trade = db.query(models.Trade).filter(models.Trade.id == old_trade_id).first()

        # Do data operations
        closing_trade.closing_premium = closing_premium
        closing_trade.num_contracts = rolled_contracts
        closing_trade.total_premium_received = (old_opening_premium - closing_premium) * closing_trade.num_contracts
        closing_trade.status = "Closed"
        ## Add the closing date
    
    # Commit the transaction
    db.commit()
    
    # Retrieve the strategy by the strategy_id
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    
    # Update the total_premium_received attribute of the strategy
    strategy.update_total_premium_received(db)
    strategy.update_average_cost_basis(db)
    strategy.update_new_cost_basis(db)

    print(strategy.total_premium_received)

    # Things to test when I'm done
    # _X__ old trade closed
    # _X__ new trade opened
    # _X__ total_premium recalculated
    # _X__ Make sure it handles correctly when not all contracts are rolled
    
    # Redirect the user to the root menu using GET method
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)