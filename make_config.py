from configparser import ConfigParser
import os
config = ConfigParser()

config['APP'] = {
    'SECRET_KEY': os.urandom(32).hex(),
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///db.sqlite3",
    'ADMINS' : ['email@email.com']
}
config['GOOGLE'] = {
    'CLIENT_ID': '',
    'CLIENT_SECRET' : ""
}

with open('./config.ini','w') as f:
    config.write(f)