import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Initialize extensions
db=SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
cors=CORS()     
load_dotenv()

def create_app(test_config=None):
    # Configure logging:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting application")

    app = Flask(__name__)

    # Configure app settings:
    if not test_config:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_TEST_DATABASE_URI")
        
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') 
    app.config['OPENWEATHER_API_KEY'] = os.environ.get('OPENWEATHER_API_KEY') 
    # Access Yelp environment variables:
    app.config['YELP_API_KEY'] = os.getenv('YELP_API_KEY')
    app.config['YELP_API_URL'] = os.getenv('YELP_API_URL')

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Import and register routes:
    logging.debug("Importing and registering routes...")
    from app.routes.auth_routes import auth
    app.register_blueprint(auth)
    
    from app.routes.expense_routes import expense
    app.register_blueprint(expense)

    from app.routes.packing_list_routes import packing_list_bp
    app.register_blueprint(packing_list_bp)

    from app.routes.item_routes import item_bp
    app.register_blueprint(item_bp)

    from app.routes.weather_routes import weather
    app.register_blueprint(weather)

    from app.routes.dining_routes import dining_routes_bp
    app.register_blueprint(dining_routes_bp)


    # Import models:
    logging.debug("Importing models...")
    from app.models.user import User
    from app.models.expense import Expense
    from app.models.packing_list import PackingList
    from app.models.item import Item
    
    logging.debug("Application setup complete")
    return app
