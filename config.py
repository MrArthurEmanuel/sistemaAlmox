import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:teste123@localhost:5432/almoxarifado'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
