from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
    )
from blacklist import BLACKLIST
from models.user import UserModel

# private variables using underscore
_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username",
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
_user_parser.add_argument("password",
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
# user register
class UserRegister(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        # avoid creating duplicate username
        if UserModel.find_by_username(data['username']):
            return {"message": "The username is already exists"}, 400  # bad request from client

        # user = UserModel(data['username'], data['password'])
        user = UserModel(**data) # same as line above
        user.save_to_db()

        return {"message": "User created successfully."}, 201  # 201: created

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200
    
    
class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        
        # find user in DB
        user = UserModel.find_by_username(data['username'])
        
        # check password. Same as `authenticate()` function
        if user and user.password == data['password']:
            # Same as `itentity()` function
            access_token = create_access_token(identity={'user_id': user.id,
                                                         'message': 'hello',
                                                         'hehe': 'hihi'}, fresh=True) # store user_id into the access_token
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': 'Invalid credential'}, 401 # Unauthorized        

class UserLogout(Resource):
    @jwt_required()
    def logout(self):
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out'}
        

# create refresh token (we'll look at this later)
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200