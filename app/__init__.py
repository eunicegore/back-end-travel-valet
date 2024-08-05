import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os


db=SQLAlchemy()
migrate=Migrate()
jwt=JWTManager()
cors=CORS()
load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)  # Allow cross-origin requests

    if not test_config:
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI")
    else:
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_TEST_DATABASE_URI")

    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    #             "SQLALCHEMY_DATABASE_URI")
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')  # Change this to a random JWT secret key


    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Import routes:
    from app.routes.auth_routes import auth
    app.register_blueprint(auth)
    
    from app.routes.expense_routes import expense
    app.register_blueprint(expense)

    from app.routes.packing_list_routes import packing_list_bp
    app.register_blueprint(packing_list_bp)

    from app.routes.packing_list_item_routes import packing_list_item_bp
    app.register_blueprint(packing_list_item_bp)

    # Import models:
    from app.models.user import User
    from app.models.expense import Expense
    from app.models.packing_list import PackingList
    from app.models.packing_list_item import PackingListItem

    
    return app
