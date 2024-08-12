from app import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    packed = db.Column(db.Boolean, default=False)
    listId = db.Column(db.Integer, db.ForeignKey('packing_list.id'), nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'quantity': self.quantity,
            'packed': self.packed,
            'listId':self.listId   # Association with the parent packing list
        }