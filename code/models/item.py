from db import db

class ItemModel(db.Model):
    
    # Create an items table with 3 columns(id, name, price)
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # this variable holds the store_id in the stores table where this item belongs to.
    store = db.relationship('StoreModel')
    
    
    def __init__(self, name, price, store_id):
        self.name = name
        self.price = price
        self.store_id = store_id
    
    # return a json representation of model (jsonify(dictionary))
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'store_id': self.store_id,
        }
    
    @classmethod
    def find_by_name(cls, name):
        # returns an ItemModel Object with price and name
        return cls.query.filter_by(name=name).first() # SELECT * FROM items WHERE name=name LIMIT 1 HOLY SHEEEEEEET!
    
    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()