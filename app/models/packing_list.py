from app import db

class PackingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    items = db.relationship('PackingListItem', backref='packing_list', lazy=True, cascade='all, delete-orphan')

# Converts PackingList instance into a dictionary:
# Helps with serialization to send data as JSON in API responses.
    def to_dict(self):
        return {
            'id': self.id,
            'list_name': self.list_name,
            'items': [item.to_dict() for item in self.items]
        }