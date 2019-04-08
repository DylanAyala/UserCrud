from flask import request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token, jwt_refresh_token_required,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from Conf import Config
from Service import User
import datetime


def user(app):
    # Setup the Flask-JWT-Extended extension
    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
    app.config["MONGO_URI"] = Config.MONGO
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']

    jwt = JWTManager(app)
    mongo = PyMongo(app)

    # Provide a method to create access tokens. The create_access_token()
    # function is used to actually generate the token, and you can return
    # it to the caller however you choose.
    @app.route('/login', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400

        users = User.user(mongo, username, password)

        if users == None:
            return jsonify({"msg": "Usuario o contraseña invalidas"})

        # Identity can be any data that is json serializable
        expires = datetime.timedelta(hours=Config.TOKEN_TIME)
        access_token = create_access_token(identity=username,
                                           expires_delta=expires)
        refresh_token = create_refresh_token(identity=username)
        login = jsonify({'login': True})
        set_access_cookies(login, access_token)
        set_refresh_cookies(login, refresh_token)
        ret = {
            'access_token': create_access_token(identity=username),
            'refresh_token': create_refresh_token(identity=username)
        }
        return jsonify(ret), 200

    @app.route('/token/remove', methods=['POST'])
    def logout():
        return jsonify({"msg": True}), 200

    @app.route('/token/refresh', methods=['POST'])
    @jwt_refresh_token_required
    def refresh():
        # Create the new access token
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        # Set the JWT access cookie in the response
        resp = jsonify({'refresh': True})
        set_access_cookies(resp, access_token)
        return resp, 200

    # Protect a view with jwt_required, which requires a valid access token
    # in the request to access.
    @app.route('/protected', methods=['GET'])
    @jwt_required
    def protected():
        # Access the identity of the current user with get_jwt_identity
        current_user = get_jwt_identity()
        refresh
        return jsonify(logged_in_as=current_user), 200
