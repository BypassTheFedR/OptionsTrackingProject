# Comment out modules not needed if you receive errors
from pytz import timezone
from typing import Optional

from fastapi import FastAPI, Request, Header, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from jinja2 import Environment

from sql_app.database import SessionLocal, engine
from sql_app import models
from sql_app import historical

# models.Base.metadata.create_all(engine)
# historical.update_prices()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_generator = get_db()
db = next(db_generator)

strategies = db.query(models.Strategy).filter(models.Strategy.status == "Open").all()
prices = db.query(models.Prices).all()
strategy_type = db.query(models.Trade.trade_type).join(models.Strategy).filter(models.Trade.strategy_id == models.Strategy.id).order_by(desc(models.Trade.id)).first()



for strategy in strategies:
    print(strategy.id)
    print(strategy.underlying)
    strategy_type = db.query(models.Trade.trade_type).filter(models.Trade.strategy_id == strategy.id).order_by(desc(models.Trade.id)).first()
    print(strategy_type[0])
    last_price_query = db.query(models.Prices).filter(models.Prices.strategy_id == strategy.id).order_by(desc(models.Prices.id)).first()
    print(last_price_query.price)