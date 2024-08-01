from app import db

class PackingListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    packed_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_packed = db.Column(db.Boolean, default=False)
    
    packing_list_id = db.Column(db.Integer, db.ForeignKey('packing_list.id'), nullable=False)


    def to_dict(self):
        return {
            'item_id': self.id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'packed_quantity': self.packed_quantity,
            'is_packed': self.is_packed
        }
