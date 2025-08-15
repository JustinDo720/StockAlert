from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, Enum
import enum

# Initialize App 
app = FastAPI()

# ---- SQLAlchemy Setup ----
DATAABASE_URI = 'sqlite:///./user_service.db'
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


class Ticker(Base):
    __tablename__ = 'tickers'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, unique=True)


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

# ---- Creating Database Models ----
Base.metadata.create_all(bind=engine)