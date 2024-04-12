#############################################################################
## Option tracking software made by Chaotic Neutral                        ##
## Start the app on localhost by running from the main direcotry           ##
##    uvicorn sql_app.main:app --reload                                    ##
## Serve the app to the local network by running:                          ## 
##    uvicorn main:app --reload -- host 0.0.0.0 --port 8000                ##
## Documentation inprogress                                                ##
############################################################################# 

import logging
import schedule
import time
from threading import Thread
from datetime import datetime, timedelta
from pytz import timezone
from typing import Optional

from fastapi import FastAPI, Request, Header, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from pydantic import BaseModel
from jinja2 import Environment

from sql_app.database import SessionLocal, engine
from sql_app import models
from sql_app import historical

models.Base.metadata.create_all(bind=engine)

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

def run_scheduler():
    # Schedule the update_prices_daily function to run daily at 1:30 PM PST
    schedule.every().day.at('13:30').do(update_prices_daily)

    # Run the schedule in a separate thread
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start the schedule in a separate thread
scheduler_thread = Thread(target=run_scheduler)
scheduler_thread.start()

# configure logging
logging.basicConfig(level=logging.INFO)

# Define a logger
logger = logging.getLogger(__name__)

app = FastAPI()

# Mapped to the templates folder in my apps directory
templates = Jinja2Templates(directory="sql_app/templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/index/', response_class=HTMLResponse)
async def strategy_list(
    request: Request, 
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    page: int = 1
):
    strategies = db.query(models.Strategy).all()
    # print(strategies)
    
    context = {'request': request, 'strategies': strategies, "page": page}
    if hx_request:
        return templates.TemplateResponse("table.html", context)

    return templates.TemplateResponse("index.html", context)

@app.get('/main/', response_class=HTMLResponse)
async def home_page(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    strategies = db.query(models.Strategy).all()
    prices = db.query(models.Prices).all()

    # Notes for testing and future capabilities:
    # Need to test total_gain is calculated correctly

    for strategy in strategies:
        total_gained = 0.0

        # Get the last trade associated with the strategy
        last_trade = strategy.trades[-1] if strategy.trades else None

        if last_trade:
            if last_trade.trade_type == 'call':
                print('call')
                total_gained = (strategy.prices[-1] - strategy.initial_cost_basis + strategy.total_premium_received)
            elif last_trade.trade_type == 'put':
                print('put')
                total_gained = strategy.total_premium_received
        
        strategy.total_gained = total_gained

    context = {'request': request, 'strategies': strategies, 'prices' : prices}
    
    if hx_request:
        return templates.TemplateResponse("table_main.html", context)
    
    return templates.TemplateResponse("main.html", context)

@app.get("/add_strategy/")
async def add_strategy_form(request: Request):
    return templates.TemplateResponse("add_strategy.html", {"request" : request})

@app.post("/add_strategy/")
async def add_strategy(
    request: Request,
    underlying: str = Form(...),
    initial_cost_basis: float = Form(...),
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
        initial_cost_basis=initial_cost_basis,
        initial_trade_date=formatted_date
    )
    
    # Add the new Strategy object to the session
    db.add(new_strategy)
    
    # Commit the transaction
    db.commit()
    db.refresh(new_strategy)
    
    # Redirect the user to the main page using GET method
    return RedirectResponse(url="/main/", status_code=status.HTTP_303_SEE_OTHER)

class add_strategy(BaseModel):
    underlying: str 
    initial_cost_basis: float
    initial_trade_date: str

@app.get('/update_prices')
async def update_prices():
    # Updates the price of current strategies
    historical.update_prices()

    # Return to main page
    return RedirectResponse(url="/main/")

