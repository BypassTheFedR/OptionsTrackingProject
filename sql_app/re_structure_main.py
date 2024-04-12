#############################################################################
## Option tracking software made by Chaotic Neutral                        ##
## Start the app on localhost by running from the main direcotry           ##
##    uvicorn sql_app.main:app --reload                                    ##
## Serve the app to the local network by running:                          ## 
##    uvicorn sql_app.main:app --reload -- host 0.0.0.0 --port 8000        ##
## Documentation inprogress                                                ##
############################################################################# 


from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from .database import SessionLocal, engine
from . import models

models.Base.metadata.create_all(bind=engine)

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

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    num_strategies = db.query(models.Strategy).count()
    if num_strategies == 0:
        strategies = [
         {'underlying': 'AAPL', 'initial_cost_basis': 170.00, 'initial_trade_date' : '3/22/2024', 'total_premium_received': 1.00},
         {'underlying': 'RBLX', 'initial_cost_basis': 45.00, 'initial_trade_date' : '3/22/2024', 'total_premium_received': .50},
         {'underlying': 'LCID', 'initial_cost_basis': 10.00, 'initial_trade_date' : '3/22/2024', 'total_premium_received': .10}
        ]
        for strategy in strategies:
            db.add(models.Strategy(**strategy))
        db.commit()
        db.close()
    else:
        print(f"{num_strategies} files already in DB")

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
    context = {'request': request, 'strategies': strategies}
    
    if hx_request:
        return templates.TemplateResponse("table_main.html", context)
    
    return templates.TemplateResponse("main.html", context)