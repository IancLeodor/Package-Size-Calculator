import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:aaaaaaaaaa@localhost/cube_calculator'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
