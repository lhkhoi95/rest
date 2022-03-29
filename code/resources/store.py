from flask_restful import Resource
from models.store import StoreModel

# extends Resource class
class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        else:
            # return a tuple with dict first, and 404 later
            return {'message': 'Store not found'}, 404 # not found
    
    def post(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {'message': "Store '{}' already exists".format(name)}, 400 # bad request from client
        # create a new store
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {'message': 'Error occurred while creating a store'}, 500 # internal server error    
        
        return store.json(), 201 # Created
    
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            
        return {'message': 'Store deleted'}
    
class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}