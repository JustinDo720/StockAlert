from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
 
# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./ticker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models 
class TickerModel(db.Model):
    # Be sure to name the table just like FastAPI expects 
    __tablename__ = 'ticker'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(15), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol
        }

# Configuration for Flask RESTful API
api = Api(app)

with app.app_context():
    # Create the database tables
    db.create_all()

class Ticker(Resource):
    def post(self):
        data = request.get_json() 
        new_ticker_instance = TickerModel(symbol=data['symbol'])
        
        # Add to DB
        db.session.add(new_ticker_instance)
        db.session.commit()
        return {
            'message': 'Ticker added successfully',
            'ticker': new_ticker_instance.to_dict()
        }

# Resource Routing 
api.add_resource(Ticker, '/tickers')
    
if __name__ == '__main__':
    app.run()
