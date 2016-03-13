from dbmodel import Base, User, Request, Proposal
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask.ext.httpauth import HTTPBasicAuth
import json

#aouth imports
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


# CLIENT_ID = json.loads(
#     open('client_secrets.json', 'r').read())['web']['client_id']

@auth.verify_password
def verify_password(username_or_token, password):
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/clientOAuth')
def start():
    return render_template('clientOAuth.html')

@app.route('/oauth/<provider>', methods = ['POST'])
def login(provider):
    #STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    print "Step 1 - Complete, received auth code %s" % auth_code
    if provider == 'google':
        #STEP 2 - Exchange for a token
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
       
        print "Step 2 Complete! Access Token : %s " % credentials.access_token

        #STEP 3 - Find User or make a new one 
        #Get user info
        h = httplib2.Http()
        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']
        
        # Si el usuario no existe, en ese momento lo registra
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username = name, picture = picture, email = email)
            session.add(user)
            session.commit()

        #STEP 4 - Make token
        token = user.generate_auth_token(600)

        #STEP 5 - Send back token to the client 
        return jsonify({'token': token.decode('ascii')})
        
        #return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'

@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@app.route('/users', methods = ['GET','POST','PUT'])
def users():
	if request.method == 'GET':
		users = getAllusers()
		return jsonify(users = [user.serialize for user in users])
	elif request.method == 'POST':
		username = request.json.get('username')
		password = request.json.get('password')
		email = request.json.get('email')
		picture = request.json.get('picture')

		if username is None or password is None:
		    abort(400) 

		user = getUserByUsername(username)

		if user is None:
			addUser(username, password, email, picture)
		else:
			return jsonify({'message':'user already exists'}), 200
		return jsonify({ 'username': username }), 201
	elif request.method == 'PUT':
		username = request.json.get('username')
		password = request.json.get('password')
		email = request.json.get('email')
		picture = request.json.get('picture')
		updated = updateUser(username, password, email, picture)
		if updated == False:
			return jsonify({ 'message': 'user not found' }), 404
		return jsonify({ 'username': username }), 204


@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

def getAllusers():
	users = session.query(User).all()
	return users

def addUser(username, password, email, picture):
	user = User()
	user.username = username
	user.email = email
	user.picture = picture
	user.hash_password(password)
	session.add(user)
	session.commit()

def updateUser(username, password, email, picture):
	user = getUserByUsername(username)
	if user is None:
		return False
	user.password = password
	user.email = email
	user.picture = picture
	session.commit()
	return True

def getUserByUsername(username):
	user = session.query(User).filter_by(username = username).first()
	return user

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)