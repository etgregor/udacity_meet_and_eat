from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()

class User(Base):
	"""Tabla para guardar usuarios"""
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	username = Column(String(32), index = True)
	password_hash = Column(String(64))
	email = Column(String)
	picture = Column(String)
	
	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

class MeetRequest(Base):
  __tablename__ = 'request'
  user_id = Column(Integer, primary_key = True)
  meal_type = Column(String)
  meal_time = Column(String)
  place_address = Column(String)
  place_image = Column(String)
  place_latitude = Column(Float)
  place_longitude = Column(Float)
  
  
  
  
  #Add a property decorator to serialize information from this database
  @property
  def serialize(self):
    return {
      'restaurant_name': self.restaurant_name,
      'restaurant_address': self.restaurant_address,
      'restaurant_image' : self.restaurant_image,
      'id' : self.id
      }

engine = create_engine('sqlite:///meerandeat.db')
 

Base.metadata.create_all(engine)