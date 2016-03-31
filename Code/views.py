# coding=utf-8
from ratelimit import *
from dbmodel import Base, User, Request, Proposal
from googleclient import GoogleClient
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect, url_for, send_from_directory

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

@app.route('/static/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

@auth.verify_password
def verify_password(email_or_token, password):
    user_id = User.verify_auth_token(email_or_token)

    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(email=email_or_token).first()

        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

# ================================== Vistas  publicas ==================================
@ratelimit(limit=300, per=30 * 1)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@ratelimit(limit=300, per=30 * 1)
@app.route('/loginview')
def loginview():
    return render_template('loginview.html')

# ================================== Vistas  protegidas ==================================

@ratelimit(limit=300, per=30 * 1)
@app.route('/requestform')
@auth.login_required
def getraddequestform():
    return render_template('addrequestform.html')


@ratelimit(limit=300, per=30 * 1)
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
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User()
            user.email = email
            user.name = name
            user.picture = picture
            session.add(user)
            session.commit()
        # STEP 4 - Make token
        token = user.generate_auth_token()

        # STEP 5 - Send back token to the client
        return jsonify({'token': token.decode('ascii')})
    elif 'local':
        email = request.json.get('email')
        password = request.json.get('password')
        user = session.query(User).filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return jsonify( error = {'code': 'InvalidUserPassword', 'message': 'Usuario y/o contraseña incorrecto'}), 401

        token = user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})

    else:
        return jsonify(json = {'code': 'InvalidProvider', 'message': 'Proveedor de autenticaicón incorrecto'}), 400

# ================================== INICIA LA API ==================================
# ***************************** Seguridad *****************************

@ratelimit(limit=300, per=30 * 1)
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/me')
@auth.login_required
def get_my_profile():
    return jsonify(g.user.serialize)


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/me', methods=['PUT'])
@auth.login_required
def update_my_profile():
    name = request.json.get('name')
    picture = request.json.get('picture')

    user = session.query(User).filter_by(email=g.user.email).first()

    if user is None:
        return jsonify(error={'code': 'UserNotFound', 'message': 'user not found'}), 404

    user.name = name
    user.picture = picture
    session.commit()
    return jsonify({'email': user.email}), 201

# ***************************** Usuarios  *****************************

@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/users', methods=['GET'])
@auth.login_required
def get_all_users():
    users = session.query(User).all()
    return jsonify(users=[user.serialize for user in users])


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/users/<string:email>')
@auth.login_required
def get_user_by_id(email):
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify(error={'code': 'UserNotFound', 'message': 'user not found'}), 400
    return jsonify(user.serialize)


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/users', methods=['POST'])
#@auth.login_required
def add_new_user():
    email = request.json.get('email')
    password = request.json.get('password')
    name = request.json.get('name')
    picture = request.json.get('picture')

    if email is None or password is None:
        abort(400)

    user = session.query(User).filter_by(email=email).first()

    if user is None:
        user = User(email = email)
        user.hash_password(password)
        user.name = name
        user.picture = picture
        session.add(user)
        session.commit()
    else:
        return jsonify({'message': 'user already exists'}), 200

    return jsonify({'email': user.email}), 201


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/users', methods=['DELETE'])
@auth.login_required
def delete_user_by_id():
    email = request.json.get('email')
    session.query(User).filter_by(email=email).delete()
    return '', 200

# ***************************** Solicitudes *****************************

@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/myrequests')
@auth.login_required
def myrequests():
    userid = g.user.id
    requests = session.query(Request).filter_by(user_id = userid).all()
    return jsonify(requests=[r.serialize for r in requests])


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/request')
@auth.login_required
def open_requets():
    userid = g.user.id
    requests = session.query(Request).filter(Request.user_id != userid).all()
    return jsonify(requests=[r.serialize for r in requests])


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/request/<int:idrequest>')
@auth.login_required
def get_request_by_id(idrequest):
    user = session.query(Request).filter_by(id=idrequest).first()
    if not user:
        return jsonify(error={'code': 'RequestNotFound', 'message': 'request not found'}), 400
    return jsonify(user.serialize)


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/request', methods=['POST'])
@auth.login_required
def addnewrequest():

    user_id = g.user.id

    meal_type = request.json.get('meal_type')
    meal_time = request.json.get('meal_time')
    location_address = request.json.get('location_address')
    geocoding = GoogleClient()
    location = geocoding.getLocationFromAddress(address=location_address)
    if location is None:
        return jsonify(error={'code': 'AddressNotFound', 'message': 'Direcion no encontrada'}), 400

    mealrequest = Request()
    mealrequest.user_id = user_id
    mealrequest.meal_type = meal_type
    mealrequest.meal_time = meal_time
    mealrequest.location_address = location_address

    mealrequest.location_latitude = location[0]
    mealrequest.location_longitude = location[1]
    session.add(mealrequest)
    session.commit()
    return jsonify({'mealrequest': mealrequest.id}), 201


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/request', methods=['PUT'])
@auth.login_required
def updaterequest():
    user_id = g.user.id

    meal_id = request.json.get('id')
    meal_type = request.json.get('meal_type')
    meal_time = request.json.get('meal_time')
    location_address = request.json.get('location_address')

    print "Buscando: %s" % meal_id

    mealrequest = session.query(Request).filter_by(id=meal_id).filter_by(user_id = user_id).first()
    if mealrequest is None:
        return jsonify(error={'code': 'RequestNotFound', 'message': 'Request no existe'}), 404

    geocoding = GoogleClient()
    location = geocoding.getLocationFromAddress(address=location_address)
    if location is None:
        return jsonify(error={'code': 'AddressNotFound', 'message': 'Direcion no encontrada'}), 400

    mealrequest.meal_type = meal_type
    mealrequest.meal_time = meal_time
    mealrequest.location_address = location_address

    mealrequest.location_latitude = location[0]
    mealrequest.location_longitude = location[1]
    session.commit()
    return jsonify({'mealrequest': mealrequest.id}), 201


@ratelimit(limit=300, per=30 * 1)
@app.route('/api/v1/request', methods=['DELETE'])
@auth.login_required
def deleteequest():
    id = request.json.get('id')
    session.query(Request).filter_by(id=id).delete()
    session.commit()
    return '', 200

# ***************************** Propuestas *****************************

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
