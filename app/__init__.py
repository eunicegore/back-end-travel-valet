import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, decode_token
from flask_cors import CORS

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
    from app.models.user import User
    from app.models.expense import Expense

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    from .routes import auth
    app.register_blueprint(auth)

    from .routes import expense
    app.register_blueprint(expense)

   
    return app



