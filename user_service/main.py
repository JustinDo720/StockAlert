from fastapi import FastAPI, Depends
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, Enum
import enum
from typing import Generator, Optional
from pydantic import BaseModel
import requests

# Initialize App 
app = FastAPI()
FLASK_TICKER_MICROSERVICE_URL = 'http://localhost:5000'

# ---- SQLAlchemy Setup ----
DATAABASE_URI = 'sqlite:///instance/user_service.db'
# Creating the engine based off the URI
engine = create_engine(DATAABASE_URI)

# Creating the Session 
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Creating a Base for our Models 
Base = declarative_base()


# ---- Model ----
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=True) 
    # We want our User to have a one-to-many relationship 
    alerts = relationship("Alert", back_populates='user')   # back_populates is similar to related_name in Django

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }

class Ticker(Base):
    __tablename__ = 'tickers'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol
        }

# Building choices -> Similar to CharField(choices=)
class RuleType(str, enum.Enum):
    # Gives us the choices (Fixed Price, Percentage Change, Trailing)
    FIXED_PRICE = 'fixed_price'
    PERCENTAGE_CHANGE = 'percentage_change'
    TRAILING_CHANGE = 'trailing_change'


class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    # Price Rule 
    rule = Column(Enum(RuleType), nullable=False, default=RuleType.FIXED_PRICE)
    value = Column(Float, nullable=False)
    # Refers back to our User Model 
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='alerts')
    # Refers back to our Ticker Model 
    ticker_id = Column(Integer, ForeignKey('tickers.id'))
    ticker = relationship('Ticker') # One-Way Relationship we don't need ticker to be related with Alert just Alert-to-Ticker

    def to_dict(self):
        return {
            'id': self.id,
            'rule': self.rule,
            'value': self.value,
            'user_id': self.user_id,
            'user': self.user.to_dict(),
            'ticker_id': self.ticker_id,
            'ticker': self.ticker.to_dict()
        }


# ---- Creating Database Models ----
Base.metadata.create_all(bind=engine)

# ---- Generator for Databse -----
def session_generator() -> Generator:
    db = SessionLocal()
    try:
         yield db
    finally:
        db.close()

# ---- Pydantic Model ----
class UserPD(BaseModel):

    username : str 


class TickerPD(BaseModel):

    symbol: str


class AlertPD(BaseModel):
    rule: Optional[RuleType] = 'fixed_price'
    value: Optional[int] = None
    user_id: Optional[int] = None 
    ticker_symbol: Optional[str] = None 

# ---- User Controller ---
@app.get('/users')
def get_users(user_id: Optional[int]=None, db: Session = Depends(session_generator)):
    """
        Endpoint to get a specific user or return a list of all available users 
    """
    if user_id is not None:
        try:
            specific_user = db.query(User).get(user_id)
            # If our user with that id exist we'll return the details
            if specific_user is not None:
                return {
                    'user': specific_user
                }
            # By default, we'll say that the user doesn't have that ID
            return {
                'msg': "No available user with that ID"
            }
        except Exception as e:
            return {
                'msg': str(e)
            }
    else:
        # Without a user_id, we'll return all of the users in our database
        all_users = db.query(User).all()
        return {
            'users': all_users
        }
    

@app.post('/users')
def add_users(user_details: UserPD, db: Session=Depends(session_generator)):
    # From our Details we build the Model based off those details
    user_model = User(**user_details.model_dump())
    
    # Using the db to add and commit our details
    db.add(user_model)
    db.commit()

    return {
        'id': user_model.id,
        'username': user_model.username
    }

@app.put('/users')
def update_users(user_id: int, new_user_details: UserPD, db: Session=Depends(session_generator)):
    user = db.query(User).get(user_id)
    if user:
        for key, detail in new_user_details.model_dump().items():
            if detail is not None:
                # Only Update the details that were sent
                setattr(user, key,detail)
        # Commit our changes 
        db.commit() 
        db.refresh(user)

        return {
            'id': user.id,
            'username': user.username
        }
    return {
        'msg': "No available user with that ID"
    }

@app.delete('/users')
def delete_users(user_id: int, db: Session=Depends(session_generator)):
    user = db.query(User).get(user_id)
    if user:
        db.delete(user)
        db.commit()
        return {
            'msg': f'User with ID: {user_id} was removed successfully.'
        }
    return {
        'msg': "No available user with that ID"
    }

# ---- Ticker Controller ---
@app.get('/tickers')
def get_tickers(ticker_symbol: Optional[str]=None, db: Session= Depends(session_generator)):
    if ticker_symbol is not None:
        ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol.lower()).first()
        if ticker:
            return {
                'ticker': ticker.to_dict()
            }
        return {
            'msg': "No available ticker with that ID"
        }
    else: 
        ticker = db.query(Ticker).all() 
        return {
            'tickers': ticker
        }

# POSTING tickers will trigger a syncronous request to our Flask Ticker Microservice
@app.post('/tickers')
def add_tickers(ticker_details: TickerPD, db: Session=Depends(session_generator)):
    details = ticker_details.model_dump() 
    details['symbol'] = details['symbol'].lower() 

    # Need to check if our ticker already exists before adding it to our db and sending a request to our Flask Ticker Service
    existing_ticker = db.query(Ticker).filter(Ticker.symbol == details['symbol']).first()
    if existing_ticker:
        return {
            'msg': "That ticker already exists in our Database."
        }

    # Now we know for certain that the ticker doesn't exist in our database
    ticker_model = Ticker(**details)
    
    db.add(ticker_model)
    db.commit()

    # Aftering a successful post we needd to send a request to our Flask Ticker Service 
    response = requests.post(f'{FLASK_TICKER_MICROSERVICE_URL}/tickers', json={'symbol': ticker_model.symbol})
    response.raise_for_status()
    # If the request was successful we return the ticker model
    return {
        'ticker': ticker_model.to_dict()
    } if response.status_code == 200 else {
        'msg': "There was an error adding the ticker to the Flask Ticker Service"
    }

@app.put('/tickers')
def update_tickers(ticker_symbol: str, new_ticker_details: TickerPD, db: Session=Depends(session_generator)):
    ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol.lower()).first()
    new_details = new_ticker_details.model_dump()
    new_details['symbol'] = new_details['symbol'].lower()
    if ticker:
        for key, details in new_details.items():
            if details is not None:
                setattr(ticker, key, details)
        
        db.commit()
        db.refresh(ticker)

        return {
            'ticker': ticker.to_dict()
        }
    else:
        return {
            'msg': "No available ticker with that ID"
        }

@app.delete('/tickers')
def remove_tickers(ticker_symbol: str, db: Session=Depends(session_generator)):
    ticker = db.query(Ticker).filter(Ticker.symbol == ticker_symbol.lower()).first()
    if ticker:
        symbol = ticker.symbol
        db.delete(ticker)
        db.commit()
        return {
            'msg': f'Ticker with Symbol: \"{symbol}\" was removed successfully.'
        }
    return {
        'msg': "No available ticker with that ID"
    }

@app.get('/alerts')
def get_alerts(user_id: int, ticker_symbol: Optional[str] = None, db: Session = Depends(session_generator)):
    """
        We'll always need a user_id to find the alert associated with our users..

        If a ticker_symbol is provided then we'll return one singular alert otherwise we'll return all the alerts
        associated with that user 
    """
    if user_id and ticker_symbol is not None:
        # Filter via user_id and ticker_id to get a specific alert 
        specific_alert = db.query(Alert).filter(Alert.user_id == user_id, Alert.ticker.has(symbol = ticker_symbol.lower())).first() 

        if specific_alert:
            return {
                'alert': specific_alert.to_dict()
            }
        # There are no alerts with the requested user_id and ticker_id 
        return {
            'msg': "No available alert with that ticker Symbol and user ID"
        }
    else:
        # We return all of our user's alerts 
        user_alerts = db.query(Alert).filter(Alert.user_id == user_id)
        return {
            'alerts': [alert.to_dict() for alert in user_alerts]
        }
    
@app.post('/alerts')
def add_alert(alert_details: AlertPD, db: Session = Depends(session_generator)):
    details = alert_details.model_dump()

    # Since our PD has a ticker_symbol we must check for that symbol and find the id
    ticker = db.query(Ticker).filter(Ticker.symbol == details['ticker_symbol'].lower()).first()
    if ticker:
        # We need to replace 'ticker_symbol' key with 'ticker_id'
        refined_details = {key: detail for key,detail in details.items() if key != 'ticker_symbol'}
        refined_details['ticker_id'] = ticker.id

        # Using the new details with the right ticker id to POST our alert 
        alert_instance = Alert(**refined_details)
        db.add(alert_instance)
        db.commit()

        return {
            'alert': alert_instance.to_dict()
        }

    return {
        'msg': "That ticker symbol does not exist in our Database."
    }

@app.put('/alerts')
def update_alert(user_id: int, ticker_symbol: str, alert_details: AlertPD, db: Session = Depends(session_generator)):
    alert = db.query(Alert).filter(Alert.user_id == user_id, Alert.ticker.has(symbol = ticker_symbol.lower())).first()

    for key, detail in alert_details.model_dump().items():
        if detail is not None:
            # Make sure it isn't a change to the ticker 
            if key == 'ticker_symbol':
                # Find the ticker and update the ticker_id as ticker_symbol doesn't exist as a field in our Alert model 
                #
                # ticker_symbol is just an easier way to find the ticker as opposed to ticker_id 
                ticker = db.query(Ticker).filter(Ticker.symbol == detail.lower()).first()
                if ticker:
                    # Make sure our ticker exists before changing the ticker_id 
                    setattr(alert, 'ticker_id', ticker.id)
            else: 
                # Good to use set attribute 
                setattr(alert, key, detail)

    # Always update in our database 
    db.commit() 
    db.refresh(alert)
    return {
        'alert': alert.to_dict()
    }

@app.delete('/alerts')
def delete_alert(user_id: int, ticker_symbol: str, db: Session = Depends(session_generator)):
    alert = db.query(Alert).filter((Alert.user_id == user_id) & (Alert.ticker.has(symbol=ticker_symbol.lower()))).first()
    if alert:
        db.delete(alert)
        db.commit() 
        return {
            'msg': f"An alert for user id: {user_id} with a ticker symbol: {ticker_symbol.upper()} was removed successfully."
        }
    return {
            'msg': f"An alert for user id: {user_id} with a ticker symbol: {ticker_symbol.upper()} does not exist."
        }