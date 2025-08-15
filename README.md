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

