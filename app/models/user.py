from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# class User(UserMixin, db.Model):
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    # Defines one-to-many relationship to PackingList model:
    packing_lists = db.relationship('PackingList', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
 
        return {
            "id": self.id,
            "name": self.username,
            "email": self.email          
        }