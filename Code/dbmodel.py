from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class User(Base):
  """Tabla para guardar usuarios"""
  __tablename__ = 'user'
  id = Column(Integer, primary_key = True)
  username = Column(String(32), index = True)
  password_hash = Column(String(64))
  email = Column(String)
  picture = Column(String)
  request = relationship('Request')
  
  def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

  def verify_password(self, password):
    return pwd_context.verify(password, self.password_hash)

  def generate_auth_token(self, expiration=600):
    s = Serializer(secret_key, expires_in = expiration)
    return s.dumps({'id': self.id })

  @staticmethod
  def verify_auth_token(token):
    s = Serializer(secret_key)
    try:
      data = s.loads(token)
    except SignatureExpired:
    #Valid Token, but expired
      return None
    except BadSignature:
    #Invalid Token
      return None
    user_id = data['id']
    return user_id
    
  @property
  def serialize(self):
    return {
      'id' : self.id,
      'username': self.username,
      'email': self.email,
      'picture' : self.picture
      }

class Request(Base):
  __tablename__ = 'request'
  id = Column(Integer, primary_key = True)
  user_id = Column(Integer, ForeignKey('user.id'), index = True, nullable = False)
  meal_type = Column(String, nullable = False)
  meal_time = Column(String, nullable = False)
  location_address = Column(String, nullable = False)
  location_latitude = Column(Float, nullable = False)
  location_longitude = Column(Float, nullable = False)
  proporal = relationship('Proposal')
 
  @property
  def serialize(self):
    return {
      'id' : self.id,
      'user_id': self.user_id,
      'meal_type': self.meal_type,
      'meal_time' : self.meal_time,
      'location_address' : self.location_address,
      'location_latitude' : self.location_latitude,
      'location_longitude' : self.location_longitude
      }

class Proposal(Base):
  __tablename__ = 'proposal'
  id = Column(Integer, primary_key = True)
  request_id = Column(Integer, ForeignKey("request.id"), index = True, nullable = False)
  user_proposed_to = Column(Integer, ForeignKey("user.id"), index = True, nullable = False)
  user_proposed_from = Column(Integer, ForeignKey("user.id"), index = True, nullable = False)

  @property
  def serialize(self):
    return {
      'id' : self.id,
      'request_id': self.request_id,
      'user_proposed_to': self.user_proposed_to,
      'user_proposed_from' : self.user_proposed_from
      }

class MealDate(Base):
  __tablename__ = 'mealdate'
  id = Column(Integer, primary_key = True)
  user_1 = Column(Integer, ForeignKey("user.id"), index = True,  nullable = False)
  user_2 = Column(Integer, ForeignKey("user.id"), index = True, nullable = False)
  restaurant_name = Column(String)
  restaurant_address = Column(String)
  restaurant_picture = Column(String)
  meal_time = Column(String)

  @property
  def serialize(self):
    return {
      'id' : self.id,
      'user_1': self.user_1,
      'user_2': self.user_2,
      'restaurant_name' : self.restaurant_name,
      'restaurant_address': self.restaurant_address,
      'restaurant_picture': self.restaurant_picture,
      'meal_time' : self.meal_time
      }

engine = create_engine('sqlite:///mealAndEat.db')
 
Base.metadata.create_all(engine)