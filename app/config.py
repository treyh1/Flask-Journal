import os

class Config(object):
	SECRET_KEY='dev123'
	USERNAME='gdos'
	PASSWORD='pumpk1npr3sch00l!'
	SQLALCHEMY_DATABASE_URI='postgresql://hklqsmvwmmlire:38c4eead7b759074bef4b6b6b56650ccdabb7fb7aefdd1ae4fde9d361a3886e2@ec2-107-20-250-195.compute-1.amazonaws.com:5432/dfbkcsjmohd6q2'
	SQLALCHEMY_TRACK_MODIFICATIONS=False
	SQLALCHEMY_ECHO = True