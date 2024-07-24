from app import db

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # user = db.relationship("User", back_populates="expenses")
    category=db.Column(db.String(100), nullable=False)

    # def to_dict(self):
 
    #     return {
    #         "id": self.id,
    #         "amount": self.amount,
    #         "description": self.description,
    #         "user_id": self.user_id,
    #         "date": self.date,
    #         "category": self.category
            
    #     }