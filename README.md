# Stock Price Alert 

## Project Objective 

Microservices-based application that enables users to **set price alerts** for selected stock ticker. When the stock price meets the specified threshold, the system will trigger a notification.This project serves as a refresher on microservice technologies. 

## Tech Stack 

**FastAPI** 
- Handles User Services 
- Handles User Management of stock price alert rules 

**Flask**
- Fetches stock prices via **Finnhub API** 
  
**Kafka**
- Async Communication between both our microservices 

**SqlAlchemy**
- Database to store our information 

**Docker + K8s**
- Docker compose to wrap everything in one containerized application 
- Scaled with Kubernetes as a orchestrator 

## Development Phase 

**08/15**
- Starting with FastAPI for user services 
    - `pip install fastapi; uvicorn; sqlalchemy`
**Expectations**
- [x] User Registrations 
- [x] User Updates Their Tickers 
- [ ] User Set Price Alerts
  - Fixed Price Target 
  - Percentage Change 
  - Trailing Change 

The idea here is to have **Users** build **Price Alerts** for their **Tickers**. Not necessarily required for Users to have a One-to-Many with Tickers but rather **One-to-Many with Alerts**


**08/18**
- SQLAlchemy set up 
- Primary Objective: Build an endpoint for Users to alter their alerts 


**FastAPI Review**

*Session Generator*

```py
from typing import Depends, Generator 
from sqlalchemy.orm import Session 

def session_gen() -> Generator:
  try:
    db = SessionLocal()
    yield db 
  finally:
    db.close

@app.get('/endpoint')
def endpoint_view(session: Session=Depends(session_gen)):
  pass
```


*Basic Queries*

```py
session.query(Model).get(paramater_int)
```

*Optioanl Parameters* 

```py
from typing import Optional

@app.get('/endpoint')
def endpoint_view(optioanl_id: Optional[int]=None, session: Session=Depends(session_gen)):
  pass
```

*Pydantic Post*

```py
from pydantic import BaseModel 

class MyPDModel(BaseModel):
    field: str | None 
  
# Usage 
@app.post('/endpoint')
def endpoint_view(details: MyPDModel, session: Session=Depends(session_gen)):
  building_model = Model(**details.model_dump())

  # Always add then commit
  session.add(building_model)
  session.commit()
```

*Pydantic Put*

```py
@app.put('/endpoint')
def endpoint_view(id: int, details: MyPDModel, session: Session=Depends(session_gen)):
  model_update = db.query(Model).get(id)

  for key, val in details.model_dump().items():
    if val is not None:
      setattr(model_update, key, val)

  db.commit()
  db.refresh(model_date)
```

*Pydantic Delete* 

```py
@app.delete('/endpoint')
def endpoint_view(id: int, session: Session=Depends(session_gen)):
  model_update = db.query(Model).get(id)

  db.delete(model_update)
  db.commit()
```

Progess:
- [x] Built CRUD 
  - User + Tickers 
- [x] Generator for Database Session 
- As for the **Alert** System 
  - You just need to supply `user_id` and `ticker_id` and SQLAlchemy will handle the relationships by themselves 
  - Create a Pydantic with these and run your usual POST view and you'll be fine.


**08/19**

Quick **note**
- Prefilling Edit forms is a **front-end responsiblity**
- However; for the Swagger UI we could make the **Pydantic fields OPTIONAL**: `ticker_symbol: Optional[str] = None` 
- This way we could work with the PUT view and remove some of the fields if we don't want to edit it 

**Filter** 
- It's important to know that `and` in a filter will evaluate True and False similar to normal python 
- If you're trying to make sure both conditions are **True** 

```py
# WRONG query
specific_alert = db.query(Alert).filter(Alert.user_id == user_id and Alert.ticker.symbol == ticker_symbol.lower()).first() 


# Use a , instead of the AND clause
specific_alert = db.query(Alert).filter(Alert.user_id == user_id, Alert.ticker.has(symbol = ticker_symbol.lower())).first() 
```
- Make sure we're using `has()` attribute since we're accessing another **FK** 

**Progress**
- [x] Alert CRUD finished 
  - Alert searches via **ticker_symbol** converted to **ticker_id** for backend POST method 
  - PUT allows optional fields via **Pydantic**  base model with **Optional** typing 
  - Queries use the `has()` function for foreign relationship and fixed the logical error using the `and` instead of a `,` or `(condition 1) & (condition 2)`