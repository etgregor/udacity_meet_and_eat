# coding=utf-8
from dbmodel import Base, User, Request, Proposal
from googleclient import GoogleClient
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask.ext.httpauth import HTTPBasicAuth
import json

# aouth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests
from ratelimit import RateLimit

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///mealAndEat.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/clientOAuth')
def start():
    return render_template('clientOAuth.html')


@app.route('/oauth/<provider>', methods=['POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # STEP 3 - Find User or make a new one
        # Get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']

        # Si el usuario no existe, en ese momento lo registra
        user = session.query(User).filter_by(username=email).first()
        if not user:
            user = adduser(email, None, name, email, picture)
        # STEP 4 - Make token
        token = user.generate_auth_token()
        # STEP 5 - Send back token to the client
        return jsonify({'token': token.decode('ascii')})
    else:
        return 'Unrecoginized Provider'


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/v1/users', methods=['GET'])
@auth.login_required
def get_allusers():
    users = getAllusers()
    return jsonify(users=[user.serialize for user in users])


@app.route('/api/v1/users', methods=['PUT'])
@auth.login_required
def update_user():
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    email = request.json.get('email')
    picture = request.json.get('picture')

    if username is None or password is None:
        abort(400)

    user = updateUser(username, password, name, email, picture)

    if user is None:
        return jsonify({'code': 'UserNotFound', 'message': 'user not found'}), 404

    return jsonify({'username': user.username}), 201


@app.route('/api/v1/users', methods=['POST'])
def add_new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    email = request.json.get('email')
    picture = request.json.get('picture')

    if username is None or password is None:
        abort(400)

    user = getUserByUsername(username)

    if user is None:
        user = adduser(username, password, name, email, picture)
    else:
        return jsonify({'message': 'user already exists'}), 200
    return jsonify({'username': user.username}), 201


@auth.login_required
@app.route('/api/v1/users/<int:id>')
def get_user_by_id(id):
    user = session.query(User).filter_by(id=id).first()
    if not user:
        return jsonify({'code': 'UserNotFound', 'message': 'user not found'}), 404
    return jsonify({'username': user.username})


@app.route('/api/v1/me')
@auth.login_required
def get_resource():
    return jsonify(g.user.serialize)

def getAllusers():
    users = session.query(User).all()
    return users


def adduser(username, password, name, email, picture):
    user = User()
    user.username = username
    user.name = name
    user.email = email
    user.picture = picture

    if password is not None:
        user.hash_password(password)

    session.add(user)
    session.commit()
    return user

def updateUser(username, password, name, email, picture):
    user = getUserByUsername(username)
    if user is None:
        return None

    if password is not None:
        user.hash_password(password)
    user.name = name
    user.email = email
    user.picture = picture
    session.commit()
    return user


def getUserByUsername(username):
    user = session.query(User).filter_by(username=username).first()
    return user


def addRequest(userId, mealType, meaiTime, locationAddress):
    geocoding = GoogleClient()
    location = geocoding.getLocationFromAddress(address=locationAddress)
    if location is None:
        raise ValueError('Dirección no encontrada en el mapa: %s' % locationAddress)

    request = Request()
    request.user_id = userId
    request.meal_type = mealType
    request.meal_time = meaiTime
    request.location_address = locationAddress
    request.location_latitude = location[0]
    request.location_longitude = location[1]
    session.add(request)
    session.commit()


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
