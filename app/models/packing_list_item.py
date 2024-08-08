from app import db

class PackingListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_packed = db.Column(db.Boolean, default=False)
    packing_list_id = db.Column(db.Integer, db.ForeignKey('packing_list.id'), nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'description': self.item_name,
            'quantity': self.quantity,
            'packed': self.is_packed,
            'listId':self.packing_list_id   # Association with the parent packing list
        }
