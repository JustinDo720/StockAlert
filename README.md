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
- [ ] User Registrations 
- [ ] User Updates Their Tickers 
- [ ] User Set Price Alerts
  - Fixed Price Target 
  - Percentage Change 
  - Trailing Change 

The idea here is to have **Users** build **Price Alerts** for their **Tickers**. Not necessarily required for Users to have a One-to-Many with Tickers but rather **One-to-Many with Alerts**


