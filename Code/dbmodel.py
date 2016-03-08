from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()

#ADD YOUR USER MODEL HERE
class User(Base):
	"""Tabla para guardar usuarios"""
	__tablename__ = 'user'
	id = Column(Integer, primary_key = True)
	username = Column(String(32), index = True)
	password_hash = Column(String(64))
	email = Column(String(40))
	picture = Column(String(200))
	
	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

engine = create_engine('sqlite:///restaruants.db')
 

Base.metadata.create_all(engine)