from datetime import datetime
from app import db

class PackingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listName = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dateSaved = db.Column(db.DateTime, default=datetime.utcnow) 
    items = db.relationship('Item', backref='packing_list', lazy=True, cascade='all, delete-orphan')

# Converts PackingList instance into a dictionary:
# Helps with serialization to send data as JSON in API responses.
    def to_dict(self):
        return {
            'id': self.id,
            'listName': self.listName,     
            'userId': self.user_id,
            'dateSaved': self.dateSaved.strftime('%Y-%m-%d'),
            'items': [item.to_dict() for item in self.items]
        }
        