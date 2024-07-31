from app import db

class PackingListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    is_packed = db.Column(db.Boolean, default=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    packed_quantity = db.Column(db.Integer, nullable=False, default=0)
    
    packing_list_id = db.Column(db.Integer, db.ForeignKey('packing_list.id'), nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'is_packed': self.is_packed,
            'quantity': self.quantity,
            'packed_quantity': self.packed_quantity
        }

