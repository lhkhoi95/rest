from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, get_jwt,
    get_jwt_identity)
from models.item import ItemModel

# Inheritance Resource class
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price",
                        type=float,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument("store_id",
                        type=int,
                        required=True,
                        help="Every item needs a store id!"
                        )

    # get an item with name.
    @jwt_required()  # need authentication
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:  # if not null
            return item.json() # item is an ItemModel objectm, we need a dictionary
        return {'message': 'Item not found'}, 404

    # create a new item
    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exitsts".format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id']) # item is type ItemModel
        try:
            item.save_to_db()
        except:
            return {'message': 'An error occurred inserting the items.'}, 500 # Internal Server Error

        return item.json(), 201

    @jwt_required()
    def delete(self, name):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        
        item = ItemModel.find_by_name(name)
        # if item exists, delete it from db
        if item:
            item.delete_from_db()
            return {'message': "Item deleted"}
        return {'message': 'Item not found'}

    # can be used to both create item or update existing item
    def put(self, name):
        # get json data from front end, and convert to dictionary
        data = self.parser.parse_args()

        # find the item with name and return
        item = ItemModel.find_by_name(name)
       
        # if not exists, save to database
        if item is None:
            item = ItemModel(name, data['price'], data['store_id']) # can do **data
        else: 
            item.price = data['price']
           
        item.save_to_db()
        
        return item.json()

class ItemList(Resource):
    @jwt_required(optional=True) # login_required
    def get(self):
        # decode access_token to retrieve user_id
        user_id = get_jwt_identity()
        print(user_id)

        # retrieve all items.
        items = [item.json() for item in ItemModel.find_all()]
        # show all items if login.
        if user_id:
            return {'items': items}, 200
        # show item names only if not login.
        return {'items': [item['name'] for item in items],
                'message': 'More data available if you log in.'}, 200 # SELECT * FROM items
