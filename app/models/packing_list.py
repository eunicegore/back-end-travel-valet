from app import db

class PackingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    is_packed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Converts PackingList instance into a dictionary:
# Helps with serialization to send data as JSON in API responses.
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'is_packed': self.is_packed,
        }