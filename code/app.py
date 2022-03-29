from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST
from db import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' # tell app.py to find data.db file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_AUTH_URL_RULE'] = '/login' # change /auth to /login
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = "khoi" # app.config['JWT_SECRET_KEY']
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app) # not creating /login


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: 
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

# if access_token is expired, send this message to user
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired',
        'error': 'token_expired'
    }), 401 # unauthorized

# this will return the message if the access_token is not matched
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401 # unauthorized

# when user doesn't send us access_token at all
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401

# when user send us non-fresh token, but we required a fresh_token
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401

# cant logout the using during the duration of access_token. Add to revoked
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "You have been logged out.",
        'error': 'token_revoked'
    }), 401

# same thing as @app.route('/item/<string:name>')
api.add_resource(Item, "/item/<string:name>")  # http://127.0.0.1:5000/item/item_name for POST
api.add_resource(ItemList, "/items")  # http://127.0.0.1:5000/item for GET
api.add_resource(UserRegister, '/register') # http://127.0.0.1:5000/item/register
api.add_resource(Store, "/store/<string:name>") # http://127.0.0.1:5000/store/<name> for POST, DELETE, PUT
api.add_resource(StoreList, "/stores") # http://127.0.0.1:5000/store for GET
api.add_resource(User, '/user/<int:user_id>') # http://127.0.0.1:5000/store for GET & DELETE
api.add_resource(UserLogin, '/login') # http://127.0.0.1:5000/login
api.add_resource(UserLogout, '/logout') # http://127.0.0.1:5000/logout
api.add_resource(TokenRefresh, '/refresh') # http://127.0.0.1:5000/refresh
if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
